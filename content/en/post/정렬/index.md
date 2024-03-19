---
title: "Simple Summary of Sorting Algorithms"
date: 2024-02-26T11:49:35+09:00
image: img/algorithm.png

tags: ["Tech Interview", "Algorithm", "Sort", "CS", "Interview"]
categories: ["Algorithm"]
---

Sorting algorithms should be chosen based on criteria such as time complexity in best, average, and worst conditions, as well as memory usage and stability.

The speed of sorting algorithms based on comparison can never be faster than ```O(nlog(n))``` in the worst case.

# List of Sorting Algorithms Covered in this Post

- Selection Sort
- Insertion Sort
- Bubble Sort
- Heap Sort
- Quick Sort
- Merge Sort
- Radix Sort

## Selection Sort

One of the simplest algorithms. Suitable for environments where copying operations are slow due to being an in-place algorithm.

At each step, the algorithm scans the array once, selects the minimum (or maximum) value among the unsorted elements, and swaps it with the element at the beginning.

After each step, the number of unsorted elements is reduced by one, and the same operation is repeated for the reduced array.

In-Place. Unstable.

### Time Complexity

| Case  | Complexity |
|:-----:|:----------:|
| Best  |  O(n^2)    |
| Worst | O(n^2)     |
| Average | O(n^2)      |

## Insertion Sort

Divides one array into a sorted and an unsorted array. Each step increases the size of the sorted array and decreases the size of the unsorted array.

The algorithm takes the first element of the unsorted array and compares it sequentially with the elements in the sorted array to insert it at the appropriate position.

In-Place. Stable.

### Time Complexity

|   Case  | Complexity |
|:-------:|:----------:|
| Best    | O(n)       |
| Worst   | O(n^2)     |
| Average | O(n^2)     |

## Bubble Sort

Linearly scans the array at each step, like bubbles rising in water, comparing and swapping adjacent elements.

In-Place. Stable.

### Time Complexity

|   Case  | Complexity |
|:-------:|:----------:|
| Best    | O(n^2)     |
| Worst   | O(n^2)     |
| Average | O(n^2)     |

## Heap Sort

Uses a max heap or min heap to sort. Can use a separate heap or modify the given array to create a heap (In-Place).

Inserting/deleting elements in a heap is O(logn) (height of the heap), and as this operation is repeated for the number of elements (twice; building the heap + removing elements from the heap), the total time complexity is O(nlogn).

In-Place. Unstable.

### Time Complexity

|   Case  | Complexity |
|:-------:|:----------:|
| Best    | O(nlogn)   |
| Worst   | O(nlogn)   |
| Average | O(nlogn)   |

## Quick Sort

Based on a pivot value, sorts elements with smaller values to the left and larger values to the right.

Recursively applies Quick Sort on each divided array until it cannot be divided anymore.

If the pivot is optimally selected at each moment, the array is divided exactly in half each time. The worst case occurs when the pivot is always selected as the minimum (or maximum) value.

In-Place. Unstable.

### Time Complexity

|   Case  | Complexity |
|:-------:|:----------:|
| Best    | O(nlogn)   |
| Worst   | O(n^2)     |
| Average | O(nlogn)   |

## Merge Sort

A divide-and-conquer algorithm. Divides the array in half and recursively applies Merge Sort to each half. Then merges the sorted arrays to get one large sorted array.

Unlike other sorting algorithms, Merge Sort has a space complexity around O(n) even in the best case.

For optimizing the sorting of the divided arrays, other sorting algorithms (such as Insertion Sort) can be mixed with Merge Sort (in this case, stability can be compromised).

Not In-Place. Stable.

### Time Complexity

|   Case  | Complexity |
|:-------:|:----------:|
| Best    | O(nlogn)   |
| Worst   | O(nlogn)   |
| Average | O(nlogn)   |

## Radix Sort

Unlike other algorithms, it sorts without comparisons. Sorts based on digits, requiring the digits to be sortable in lexicographical order.

A kind of Bucket Sort.

Not In-Place. Stable.

### Time Complexity

Let n be the number of digits to sort, d be the maximum number of digits, and k be the number of buckets (for numbers, 0-9, so 10).

Best, Worst, Average: O(d(n + k))