import os
import time
import threading
import multiprocessing
from queue import Queue

# Функція для пошуку ключових слів у файлі
def search_keywords_in_file(file_path, keywords):
    results = {keyword: [] for keyword in keywords}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            for keyword in keywords:
                if keyword in content:
                    results[keyword].append(file_path)
    except Exception as e:
        print(f"Помилка під час читання файлу {file_path}: {e}")
    return results

# Злиття результатів
def merge_results(all_results):
    merged = {}
    for result in all_results:
        for keyword, files in result.items():
            if keyword not in merged:
                merged[keyword] = []
            merged[keyword].extend(files)
    return merged

# Функція для обробки файлів у процесі
def worker_process(files, keywords, queue):
    process_results = []
    for file_path in files:
        process_results.append(search_keywords_in_file(file_path, keywords))
    queue.put(process_results)

# Багатопотоковий підхід
def multithreaded_search(file_paths, keywords):
    def worker(files, output):
        thread_results = []
        for file_path in files:
            thread_results.append(search_keywords_in_file(file_path, keywords))
        output.put(thread_results)

    num_threads = min(len(file_paths), os.cpu_count() * 2)
    threads = []
    output_queue = Queue()
    chunk_size = len(file_paths) // num_threads
    for i in range(num_threads):
        chunk = file_paths[i * chunk_size: (i + 1) * chunk_size]
        thread = threading.Thread(target=worker, args=(chunk, output_queue))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    all_results = []
    while not output_queue.empty():
        all_results.extend(output_queue.get())
    return merge_results(all_results)

# Багатопроцесорний підхід
def multiprocess_search(file_paths, keywords):
    num_processes = min(len(file_paths), os.cpu_count())
    processes = []
    queue = multiprocessing.Queue()
    chunk_size = len(file_paths) // num_processes
    for i in range(num_processes):
        chunk = file_paths[i * chunk_size: (i + 1) * chunk_size]
        process = multiprocessing.Process(target=worker_process, args=(chunk, keywords, queue))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    all_results = []
    while not queue.empty():
        all_results.extend(queue.get())
    return merge_results(all_results)

# Основна функція
if __name__ == "__main__":
    # Налаштування
    keywords = ["homework", "interesting"]  # Задати ключові слова
    directory = "test_files"  # Папка з файлами
    file_paths = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    print("=== Багатопотоковий підхід ===")
    start_time = time.time()
    thread_results = multithreaded_search(file_paths, keywords)
    end_time = time.time()
    print("Результати:", thread_results)
    print(f"Час виконання: {end_time - start_time:.2f} секунд\n")

    print("=== Багатопроцесорний підхід ===")
    start_time = time.time()
    process_results = multiprocess_search(file_paths, keywords)
    end_time = time.time()
    print("Результати:", process_results)
    print(f"Час виконання: {end_time - start_time:.2f} секунд")
