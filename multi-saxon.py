import os
import csv
import time
import threading
import logging
import multiprocessing
import xml.etree.ElementTree as ET

from tqdm import tqdm
from multiprocessing import Manager
from tqdm.contrib.concurrent import process_map

from saxonche import PySaxonProcessor, PyXslt30Processor

logging.basicConfig(filename='errors.log', level=logging.ERROR)

# global variables
root_dir = '/Users/clem/Documents/EEBO/'
output_dir = '/Users/clem/Desktop/EEBOTest4'
metadata_dir = '/Users/clem/Desktop/EEBOTest4/metadata'
xslt_file_path = '/Users/clem/Desktop/EEBOTest4/scripts/transformEEBO.xsl'
os.makedirs(metadata_dir, exist_ok=True)
csv_file_path = os.path.join(metadata_dir, 'metadata.csv')

# utility functions
def get_metadata(xml_tree):
    title_el = xml_tree.find('.//tei:titleStmt/tei:title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
    author_el = xml_tree.find('.//tei:titleStmt/tei:author', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
    date_el = xml_tree.find('.//tei:sourceDesc/tei:biblFull/tei:publicationStmt/tei:date', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
    language_el = xml_tree.find('.//tei:profileDesc/tei:langUsage/tei:language', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
    title = title_el.text if title_el is not None else "Unknown"
    author = author_el.text if author_el is not None else "Unknown"
    date = date_el.text if date_el is not None else "Unknown"
    language = language_el.get('ident') if language_el is not None else "Unknown"
    return [title, author, date, language]


def count_words_in_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    return len(text.split())


def heartbeat():
    while True:
        print(".", end="", flush=True)
        time.sleep(10)  # print a dot every 10 seconds

threading.Thread(target=heartbeat, daemon=True).start()

def process_files(file_chunk, xslt_content, progress_value):
    results = []

    # Initialize the Saxon processor for each worker
    with PySaxonProcessor(license=False) as proc:
        xslt_processor = proc.new_xslt30_processor()
        compiled_stylesheet = xslt_processor.compile_stylesheet(stylesheet_text=xslt_content)

        for filename in file_chunk:
            try:
                #print(f"Processing: {filename}") # debug
                xml_file_path = filename
                output_file_path = os.path.join(output_dir, os.path.basename(filename).replace('.xml', '.txt'))
                # Transform the XML file using the compiled
                compiled_stylesheet.transform_to_file(source_file=xml_file_path, output_file=output_file_path)

                # Parse XML and get metadata
                xml_tree = ET.parse(xml_file_path)
                metadata = get_metadata(xml_tree)

                # Create language-specific output directory
                language = metadata[3] if metadata[3] else "Unknown"
                language_dir = os.path.join(output_dir, language)
                os.makedirs(language_dir, exist_ok=True)

                output_file_path_lang = os.path.join(language_dir, os.path.basename(filename).replace('.xml', '.txt'))
                os.rename(output_file_path, output_file_path_lang)
                # Count words in TXT file
                word_count = count_words_in_file(output_file_path_lang)
                results.append(metadata + [word_count])
                progress_value.value += 1

                # Update the shared progress value
                # print(f"Updated Progress Value: {progress.value}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                logging.error(f"Error processing {filename}: {e}")

    return results

def wrapper(args):
    return process_files(*args)

if __name__ == '__main__':
    try:
        all_files = [os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(root_dir) for filename in filenames if filename.endswith('.xml')]
        num_processes = multiprocessing.cpu_count()
        with Manager() as manager:
            progress_value = manager.Value('i', 0)

            pbar = tqdm(total=len(all_files))

            def update_progress_bar(progress_value):
                while True:
                    pbar.update(progress_value.value - pbar.n)
                    time.sleep(0.5)

            progress_thread = threading.Thread(target=update_progress_bar, args=(progress_value,), daemon=True)
            progress_thread.start()

            chunks = [all_files[i::num_processes] for i in range(num_processes)]

            with open(xslt_file_path, 'r') as file:
                xslt_content = file.read()

            pool = multiprocessing.Pool(processes=num_processes)
            results = pool.map(wrapper, [(chunk, xslt_content, progress_value) for chunk in chunks])
            pool.close()
            pool.join()

        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Author", "Date", "Language", "Word Count"])
            for result_chunk in results:
                for row in result_chunk:
                    writer.writerow(row)

    except KeyboardInterrupt:
        print("\\nReceived keyboard interrupt. Exiting now...")

    finally:
        print("May the force be with you.")
