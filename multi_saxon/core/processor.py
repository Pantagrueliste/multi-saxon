"""
Core processor module for XML transformation with Saxon
"""

import os
import csv
import time
import logging
import threading
import multiprocessing
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple

from tqdm import tqdm
from multiprocessing import Manager, Pool
from saxonche import PySaxonProcessor, PyXslt30Processor

from multi_saxon.utils.config import Config
from multi_saxon.utils.file_utils import count_words_in_file, ensure_dir_exists


class SaxonProcessor:
    """
    Main processor class for XML transformation using Saxon
    """
    
    def __init__(self, config: Config):
        """
        Initialize the Saxon processor with the given configuration.
        
        Args:
            config: The configuration object
        """
        self.config = config
        self.logger = logging.getLogger("multi_saxon")
        
        # Setup logging
        self._setup_logging()
        
        # Preload XSLT content
        self.xslt_content = self._load_xslt()
        
        # Create output directory if it doesn't exist
        ensure_dir_exists(self.config.output_directory)
        ensure_dir_exists(os.path.dirname(self.config.metadata_file))
    
    def _setup_logging(self) -> None:
        """Set up logging configuration"""
        log_level = getattr(logging, self.config.log_level.upper())
        logging.basicConfig(
            filename=self.config.log_file,
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def _load_xslt(self) -> str:
        """Load the XSLT content from the specified file path"""
        try:
            with open(self.config.xslt_file_path, 'r') as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Failed to load XSLT file: {e}")
            raise
    
    def _get_metadata(self, xml_tree: ET.ElementTree) -> List[str]:
        """
        Extract metadata from the XML tree.
        
        Args:
            xml_tree: The parsed XML tree
            
        Returns:
            List of metadata elements: [title, author, date, language]
        """
        namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}
        
        title_el = xml_tree.find('.//tei:titleStmt/tei:title', namespaces=namespaces)
        author_el = xml_tree.find('.//tei:titleStmt/tei:author', namespaces=namespaces)
        date_el = xml_tree.find('.//tei:sourceDesc/tei:biblFull/tei:publicationStmt/tei:date', namespaces=namespaces)
        language_el = xml_tree.find('.//tei:profileDesc/tei:langUsage/tei:language', namespaces=namespaces)
        
        title = title_el.text if title_el is not None else "Unknown"
        author = author_el.text if author_el is not None else "Unknown"
        date = date_el.text if date_el is not None else "Unknown"
        language = language_el.get('ident') if language_el is not None else "Unknown"
        
        return [title, author, date, language]
    
    def _process_files(self, file_chunk: List[str], progress_value: multiprocessing.Value, 
                      retry_count: int = 2) -> List[List[Any]]:
        """
        Process a chunk of XML files, transform them, extract metadata, and count words.
        
        Args:
            file_chunk: List of file paths to process
            progress_value: Shared progress counter
            retry_count: Number of times to retry failed operations
            
        Returns:
            List of metadata results for each file
        """
        results = []
        
        # Initialize the Saxon processor for each worker
        with PySaxonProcessor(license=False) as proc:
            xslt_processor = proc.new_xslt30_processor()
            
            try:
                compiled_stylesheet = xslt_processor.compile_stylesheet(stylesheet_text=self.xslt_content)
            except Exception as e:
                self.logger.error(f"Failed to compile stylesheet: {e}")
                return results
            
            for xml_file_path in file_chunk:
                tries = 0
                while tries <= retry_count:
                    try:
                        output_file_path = os.path.join(
                            self.config.output_directory, 
                            os.path.basename(xml_file_path).replace('.xml', '.txt')
                        )
                        
                        # Transform the XML file using the compiled stylesheet
                        compiled_stylesheet.transform_to_file(
                            source_file=xml_file_path, 
                            output_file=output_file_path
                        )
                        
                        # Parse XML and get metadata
                        xml_tree = ET.parse(xml_file_path)
                        metadata = self._get_metadata(xml_tree)
                        
                        # Create language-specific output directory
                        language = metadata[3]
                        language_dir = os.path.join(self.config.output_directory, language)
                        ensure_dir_exists(language_dir)
                        
                        output_file_path_lang = os.path.join(
                            language_dir, 
                            os.path.basename(xml_file_path).replace('.xml', '.txt')
                        )
                        
                        os.rename(output_file_path, output_file_path_lang)
                        
                        # Count words in TXT file
                        word_count = count_words_in_file(output_file_path_lang)
                        results.append(metadata + [word_count])
                        
                        # Update progress
                        with progress_value.get_lock():
                            progress_value.value += 1
                            
                        # Success, break the retry loop
                        break
                        
                    except ET.ParseError as parse_error:
                        self.logger.error(f"XML parsing error in file {xml_file_path}: {parse_error}")
                    except FileNotFoundError as fnf_error:
                        self.logger.error(f"File not found: {xml_file_path}: {fnf_error}")
                    except IOError as io_error:
                        self.logger.error(f"IO error in file {xml_file_path}: {io_error}")
                    except Exception as exception:
                        self.logger.error(f"Unexpected error in file {xml_file_path}: {exception}")
                        
                    # Increment retry counter
                    tries += 1
                    if tries <= retry_count:
                        self.logger.info(f"Retrying file {xml_file_path} (attempt {tries+1}/{retry_count+1})")
                        time.sleep(1)  # Short delay before retry
        
        return results
    
    @staticmethod
    def _wrapper(args: Tuple) -> List[List[Any]]:
        """
        Wrapper function for process_files to unpack arguments.
        
        Args:
            args: Tuple of (processor, file_chunk, progress_value)
            
        Returns:
            Results from processing the file chunk
        """
        processor, file_chunk, progress_value = args
        return processor._process_files(file_chunk, progress_value)
    
    def _heartbeat_thread(self) -> None:
        """Print a dot every 10 seconds to indicate the script is running."""
        while not self._done_event.is_set():
            print(".", end="", flush=True)
            time.sleep(10)
    
    def _progress_thread(self, progress_value: multiprocessing.Value, pbar: tqdm) -> None:
        """Update the progress bar based on the shared progress value."""
        while not self._done_event.is_set():
            pbar.update(progress_value.value - pbar.n)
            time.sleep(0.5)
    
    def process_all(self, batch_size: Optional[int] = None) -> None:
        """
        Process all XML files in the input directory.
        
        Args:
            batch_size: Optional batch size for memory optimization. If None,
                        files will be divided equally among processors.
        """
        try:
            # Find all XML files in the input directory
            all_files = []
            self.logger.info(f"Searching for XML files in {self.config.input_directory}")
            
            for dirpath, _, filenames in os.walk(self.config.input_directory):
                for filename in filenames:
                    if filename.endswith('.xml'):
                        all_files.append(os.path.join(dirpath, filename))
                        
            self.logger.info(f"Found {len(all_files)} XML files to process")
            
            if not all_files:
                self.logger.warning("No XML files found in the input directory")
                return
            
            # Determine optimal number of processes
            num_processes = min(multiprocessing.cpu_count(), self.config.max_workers)
            self.logger.info(f"Using {num_processes} worker processes")
            
            # Set up manager for shared variables
            with Manager() as manager:
                progress_value = manager.Value('i', 0)
                self._done_event = manager.Event()
                
                # Set up progress bar
                pbar = tqdm(total=len(all_files), desc="Processing XML files")
                
                # Start heartbeat thread
                heartbeat_thread = threading.Thread(target=self._heartbeat_thread, daemon=True)
                heartbeat_thread.start()
                
                # Start progress update thread
                progress_thread = threading.Thread(
                    target=self._progress_thread,
                    args=(progress_value, pbar),
                    daemon=True
                )
                progress_thread.start()
                
                # Divide files into chunks
                if batch_size:
                    # Optimize memory usage with batching
                    chunks = [all_files[i:i + batch_size] 
                              for i in range(0, len(all_files), batch_size)]
                else:
                    # Divide files equally among processes
                    chunks = [all_files[i::num_processes] for i in range(num_processes)]
                
                # Process files in parallel
                pool = Pool(processes=num_processes)
                results = pool.map(
                    self._wrapper,
                    [(self, chunk, progress_value) for chunk in chunks]
                )
                
                # Clean up
                pool.close()
                pool.join()
                self._done_event.set()
                progress_thread.join()
                heartbeat_thread.join()
                pbar.close()
                
            # Write results to CSV
            self._write_metadata_csv(results)
            
            # Generate report
            success_count = sum(len(result_chunk) for result_chunk in results)
            self.logger.info(f"Processing complete: {success_count}/{len(all_files)} files processed successfully")
            
            # Print summary
            print(f"\nProcessing complete: {success_count}/{len(all_files)} files processed successfully")
            if success_count < len(all_files):
                print(f"Check {self.config.log_file} for details on failed files")
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt. Exiting.")
            if 'pool' in locals():
                pool.terminate()
                pool.join()
        except Exception as e:
            self.logger.error(f"Error in processing: {e}", exc_info=True)
            raise
    
    def _write_metadata_csv(self, results: List[List[List[Any]]]) -> None:
        """
        Write metadata results to CSV file.
        
        Args:
            results: List of result chunks from processing
        """
        try:
            with open(self.config.metadata_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Title", "Author", "Date", "Language", "Word Count"])
                for result_chunk in results:
                    for row in result_chunk:
                        writer.writerow(row)
            self.logger.info(f"Metadata written to {self.config.metadata_file}")
        except Exception as e:
            self.logger.error(f"Failed to write metadata to CSV: {e}")