import os
import csv
import time
import threading
import logging
import multiprocessing
import xml.etree.ElementTree as ET
import toml

from tqdm import tqdm
from multiprocessing import Manager
from tqdm.contrib.concurrent import process_map

from saxonche import PySaxonProcessor, PyXslt30Processor

# Load configuration from TOML file
config = toml.load("config.toml")

logging.basicConfig(filename=config["logging"]["filename"], level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_metadata(xml_tree: ET.ElementTree) -> list:
    """Extract metadata from the XML tree."""
    title_el = xml_tree.find('.//tei:titleStmt/tei:title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
    author_el = xml_tree.find('.//tei:titleStmt/tei:author', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
    date_el = xml_tree.find('.//tei:sourceDesc/tei:biblFull/tei:publicationStmt/tei:date', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
    language_el = xml_tree.find('.//tei:profileDesc/tei:langUsage/tei:language', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
    title = title_el.text if title_el is not None else "Unknown"
    author = author_el.text if author_el is not None else "Unknown"
    date = date_el.text if date_el is not None else "Unknown"
    language = language_el.get('ident') if language_el is not None else "Unknown"
    return [title, author, date, language]


def count_words_in_file(file_path: str) -> int:
    """Count the number of words in a file."""
    with open(file_path, 'r') as file:
        text = file.read()
    return len(text.split())


def heartbeat():
    """Print a dot every 10 seconds to indicate the script is running."""
    while True:
        print(".", end="", flush=True)
        time.sleep(10)


threading.Thread(target=heartbeat, daemon=True).start()


def process_files(file_chunk: list, xslt_content: str, progress_value: multiprocessing.Value) -> list:
    """Process a chunk of XML files, transform them, extract metadata, and count words."""
    results = []

    # Initialize the Saxon processor for each worker
    with PySaxonProcessor(license=False) as proc:
        xslt_processor = proc.new_xslt30_processor()
        compiled_stylesheet = xslt_processor.compile_stylesheet(stylesheet_text=xslt_content)

        for xml_file_path in file_chunk:
            try:
                output_file_path = os.path.join(config["output"]["directory"], os.path.basename(xml_file_path).replace('.xml', '.txt'))
                
                # Transform the XML file using the compiled stylesheet
                compiled_stylesheet.transform_to_file(source_file=xml_file_path, output_file=output_file_path)

                # Parse XML and get metadata
                xml_tree = ET.parse(xml_file_path)
                metadata = get_metadata(xml_tree)

                # Create language-specific output directory
                language = metadata[3]
                language_dir = os.path.join(config["output"]["directory"], language)
                os.makedirs(language_dir, exist_ok=True)

                output_file_path_lang = os.path.join(language_dir, os.path.basename(xml_file_path).replace('.xml', '.txt'))
                os.rename(output_file_path, output_file_path_lang)
                
                # Count words in TXT file
                word_count = count_words_in_file(output_file_path_lang)
                results.append(metadata + [word_count])
                progress_value.value += 1

            except ET.ParseError as parse_error:
                logging.error(f"XML parsing error in file {xml_file_path}: {parse_error}")
            except FileNotFoundError as fnf_error:
                logging.error(f"File not found: {xml_file_path}: {fnf_error}")
            except IOError as io_error:
                logging.error(f"IO error in file {xml_file_path}: {io_error}")
            except Exception as exception:
                logging.error(f"Unexpected error in file {xml_file_path}: {exception}")

    return results


def wrapper(args: tuple) -> list:
    """Wrapper function for process_files to unpack arguments."""
    return process_files(*args)


if __name__ == '__main__':
    try:
        all_files = [os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(config["input"]["directory"]) for filename in filenames if filename.endswith('.xml')]
        num_processes = multiprocessing.cpu_count()
        
        with Manager() as manager:
            progress_value = manager.Value('i', 0)
            done_event = manager.Event()
            pbar = tqdm(total=len(all_files))

            def update_progress_bar(progress_value: multiprocessing.Value):
                while not done_event.is_set():
                    pbar.update(progress_value.value - pbar.n)
                    time.sleep(0.5)

            progress_thread = threading.Thread(target=update_progress_bar, args=(progress_value,), daemon=True)
            progress_thread.start()

            chunks = [all_files[i::num_processes] for i in range(num_processes)]

            with open(config["xslt"]["file_path"], 'r') as file:
                xslt_content = file.read()

            pool = multiprocessing.Pool(processes=num_processes)
            results = pool.map(wrapper, [(chunk, xslt_content, progress_value) for chunk in chunks])
            pool.close()
            pool.join()
            done_event.set()
            progress_thread.join()

        with open(config["output"]["metadata_file"], 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Author", "Date", "Language", "Word Count"])
            for result_chunk in results:
                for row in result_chunk:
                    writer.writerow(row)

    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt. Exiting.")
        if 'pool' in locals():
            pool.terminate()
            pool.join()

    finally:
        logging.info("Script execution completed.")
