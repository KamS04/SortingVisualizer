import multiprocessing
from time import sleep
import threading

def swap(arr, i, j, lock, sleep_time=0):
    sleep(sleep_time)
    lock.acquire()
    arr[i], arr[j] = arr[j], arr[i]
    lock.release()

def bubble_sort(arr, lock, processes, sleep_time=0):
    lock.acquire()
    length = len(arr)
    lock.release()
    for j in range(length-1):
        for i in range(length-j-1):
            lock.acquire()
            a, b = arr[i], arr[i+1]
            lock.release()
            if a > b:
                swap(arr, i, i+1, lock, sleep_time=sleep_time)

def dual_pivot_quick_sort(arr, lock, processes, sleep_time=0):
    lock.acquire()
    length = len(arr)
    lock.release()
    _dp_quicksort(arr, 0, length-1, lock, processes, sleep_time=sleep_time)

def _dp_quicksort(arr, start, end, lock, processes, sleep_time=0):
    if (start >= end):
        return
    
    l_index, h_index = _dp_partition(arr, start, end, lock, sleep_time=sleep_time)
    
    try:
        p1 = threading.Thread(target=lambda: _dp_quicksort(arr, start, l_index-1, lock, processes, sleep_time), daemon=True)
        p2 = threading.Thread(target=lambda: _dp_quicksort(arr, l_index+1, h_index-1, lock, processes, sleep_time), daemon=True)
        p1.start()
        p2.start()
        _dp_quicksort(arr, h_index+1, end, lock, processes, sleep_time=sleep_time)
        p1.join()
        p2.join()
    except:
        _dp_quicksort(arr, start, l_index-1, lock, processes, sleep_time=sleep_time)
        _dp_quicksort(arr, l_index+1, h_index-1, lock, processes, sleep_time=sleep_time)
        _dp_quicksort(arr, h_index+1, end, lock, processes, sleep_time=sleep_time)

def _dp_partition(arr, start, end, lock, sleep_time=0):
    lock.acquire()
    s_val, e_val = arr[start], arr[end]
    lock.release()

    if s_val > e_val:
        swap(arr, start, end, lock, sleep_time=sleep_time)

    lock.acquire()
    l_pivotValue, h_pivotValue = arr[start], arr[end]
    lock.release()

    l_pivotIndex = index = start + 1
    h_pivotIndex = end - 1

    while index <= h_pivotIndex:
        lock.acquire()
        val = arr[index]
        lock.release()

        if val < l_pivotValue:
            swap(arr, index, l_pivotIndex, lock, sleep_time=sleep_time)
            l_pivotIndex += 1
        elif val >= h_pivotValue:
            lower = True
            while lower:
                lock.acquire()
                val = arr[h_pivotIndex]
                lock.release()
                if val > h_pivotValue and index < h_pivotIndex:
                    lower = True
                    h_pivotIndex -= 1
                else:
                    lower = False
            
            swap(arr, index, h_pivotIndex, lock, sleep_time=sleep_time)
            h_pivotIndex -= 1

            lock.acquire()
            val = arr[index]
            lock.release()

            if val < l_pivotValue:
                swap(arr, index, l_pivotIndex, lock, sleep_time=sleep_time)
                l_pivotIndex += 1
        
        index += 1
    
    l_pivotIndex -= 1
    h_pivotIndex += 1
    
    swap(arr, start, l_pivotIndex, lock, sleep_time=sleep_time)
    swap(arr, end, h_pivotIndex, lock, sleep_time=sleep_time)

    return l_pivotIndex, h_pivotIndex

def selection_sort(arr, lock, processes, sleep_time=0):
    lock.acquire()
    length = len(arr)
    lock.release()
    for i in range(length-1):
        min_index = i
        lock.acquire()
        current_min = arr[i]
        lock.release()
        for j in range(length-i):
            lock.acquire()
            val = arr[j+i]
            lock.release()
            if val < current_min:
                current_min = val
                min_index = j+i
        swap(arr, i, min_index, lock, sleep_time=sleep_time)

def quick_sort(arr, lock, processes, sleep_time=0):
    lock.acquire()
    length = len(arr)
    lock.release()
    _quick_sort(arr, 0, length, lock, processes, sleep_time=sleep_time)

def _quick_sort(arr, start, end, lock, processes, sleep_time=0):
    if (start >= end):
        return

    index = _qs_partition(arr, start, end, lock, sleep_time=sleep_time)

    try:
        p1 = threading.Thread(target=lambda: _quick_sort(arr, start, index, lock, processes, sleep_time), daemon=True)
        p1.start()
        _quick_sort(arr, index+1, end, lock, processes, sleep_time)
        p1.join()
    except:
        _quick_sort(arr, start, index, lock, processes, sleep_time=sleep_time)
        _quick_sort(arr, index+1, end, lock, processes, sleep_time=sleep_time)

def _qs_partition(arr, start, end, lock, sleep_time=0):
    pivotIndex = start
    
    lock.acquire()
    pivotValue = arr[end-1]
    lock.release()

    for i in range(start, end):
        lock.acquire()
        val = arr[i]
        lock.release()

        if val < pivotValue:
            swap(arr, i, pivotIndex, lock, sleep_time=sleep_time)
            pivotIndex += 1

    swap(arr, pivotIndex, end-1, lock, sleep_time=sleep_time)
    return pivotIndex

def merge_sort(arr, lock, processes, sleep_time=0):
    lock.acquire()
    length = len(arr)
    lock.release()
    mid = length // 2
    _merge_sort(arr, 0, mid, length, lock, processes, sleep_time=sleep_time)

def _merge_sort(arr, start, mid, end, lock, processes, sleep_time=0):
    if end - start > 1:
        low_mid = (mid + start) // 2
        high_mid = (end + mid) // 2

        try:
            p1 = threading.Thread(target=lambda: _merge_sort(arr, start, low_mid, mid, lock, processes, sleep_time), daemon=True)
            p1.start()
            _merge_sort(arr, mid, high_mid, end, lock, processes, sleep_time=sleep_time)
            p1.join()      
        except:
            _merge_sort(arr, start, low_mid, mid, lock, processes, sleep_time=sleep_time)
            _merge_sort(arr, mid, high_mid, end, lock, processes, sleep_time=sleep_time)

        _merge(arr, start, mid, end, lock, sleep_time=sleep_time)

def _merge(arr, start, mid, end, lock, sleep_time=0):
    lock.acquire()
    arr_copy = list(arr).copy()
    lock.release()

    lp = start
    rp = mid
    for i in range(start, end):
        if lp < mid and rp < end:
            if arr_copy[lp] < arr_copy[rp]:
                lock.acquire()
                arr[i] = arr_copy[lp]
                lock.release()
                lp += 1
            else:
                lock.acquire()
                arr[i] = arr_copy[rp]
                lock.release()
                rp += 1
            sleep(sleep_time)
        elif lp < mid:
            lock.acquire()
            arr[i] = arr_copy[lp]
            lock.release()
            lp += 1
            sleep(sleep_time)
        elif rp < end:
            lock.acquire()
            arr[i] = arr_copy[rp]
            lock.release()
            rp += 1
            sleep(sleep_time)
    
    del arr_copy

algorithm_map = {'BubbleSort': bubble_sort,
                 'DualPivotQuickSort': dual_pivot_quick_sort,
                 'QuickSort': quick_sort,
                 'SelectionSort': selection_sort,
                 'MergeSort': merge_sort}