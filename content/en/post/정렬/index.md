---
title: "Simple Summary of Sorting Algorithms"
date: 2024-02-26T11:49:35+09:00
image: img/algorithm.png
 
tags: ["Tech Interview", "Algorithm", "sort", "cs", "interview"]
categories: ["Algorithm"]
---

When selecting a sorting algorithm, not only should you consider the time complexity in best, average, and worst conditions, but also factors such as memory usage and stability.

The speed of a comparison-based sorting algorithm in the worst case condition cannot be faster than ```O(nlog(n))```.

# List of Sorting Algorithms in This Post

- Selection Sort
- Insertion Sort
- Bubble Sort
- Heap Sort
- Quick Sort
- Merge Sort
- Radix Sort

## Selection Sort

One of the simplest algorithms. Suitable for environments where copying operations are slow due to being an in-place algorithm.

It scans the array once at each step, selects the minimum (or maximum) value among the unsorted elements and swaps it with the first element.

After each step, it reduces the number of unsorted elements by 1 and repeats the same operation for the reduced array.

In-Place. Unstable.

### Time Complexity
| Case |       Complexity        |
|:----:|:----------------------:|
| Best |       O(n<sup>2</sup>)       |
| Worst | O(n<sup>2</sup>) |
| Average |        O(n<sup>2</sup>)        |


## Insertion Sort

Divides one array into a sorted and an unsorted array, increasing the size of the sorted array step by step and decreasing the size of the unsorted array.

It takes the front element of the unsorted array and compares it sequentially with the elements of the sorted array until it finds the right position to insert.

In-Place. Stable.
### Time Complexity
| Case       |  Complexity        |
|:----------:|:------------------:|
| Best (Already sorted) |       O(n)       |
| Worst        | O(n<sup>2</sup>) |
| Average |        O(n<sup>2</sup>)        |

## Bubble Sort

At each step, it linearly scans the array and performs comparisons and swaps with adjacent elements similar to bubbles rising in a cylinder.

In-Place. Stable.

### Time Complexity
| Case       |       Complexity        |
|:----------:|:----------------------:|
| Best       |       O(n<sup>2</sup>)       |
| Worst     | O(n<sup>2</sup>) |
| Average |        O(n<sup>2</sup>)        |

## Heap Sort

A method of sorting using a Max Heap or Min Heap. It is possible to use a separate heap or transform the given array into a heap (In-Place).

The operations of inserting/deleting elements in a heap are ```O(logn)``` (height of the heap, a complete binary tree), and performing these operations for the number of elements (twice; making the heap + removing one element from the heap) results in an overall time complexity of ```O(nlogn)```.

In-Place. Unstable.

### Time Complexity
| Case |         Complexity        |
|:----:|:------------------------:|
| Best   |      O(nlogn)       |
| Worst |      O(nlogn)       |
| Average |      O(nlogn)       |

## Quick Sort

Divides the array into smaller arrays based on a pivot value, with smaller values on the left and larger values on the right.

For each divided array, Quick Sort is performed recursively until it cannot be divided further.

If the pivot is optimally selected at each moment, the given array is precisely halved each time. The worst case is when the pivot is always selected as the minimum value (or maximum value).

In-Place. Unstable.

### Time Complexity
| Case |       Complexity        |
|:----:|:----------------------:|
| Best   |     O(nlogn)     |
| Worst | O(n<sup>2</sup>) |
| Average | O(nlogn) |

## Merge Sort

One of the divide-and-conquer algorithms. It divides the array in half and performs Merge Sort on each divided array. Then, it merges the sorted arrays together to obtain one large sorted array.

Unlike other sorting algorithms, it has a space complexity of O(n) even in the best case.

To optimize the sorting of divided arrays, Merge Sort can be mixed with other sorting algorithms (such as Insertion Sort) based on a specific size (in this case, it may not be stable).

Not In-Place. Stable.

### Time Complexity
| Case |         Complexity         |
|:----:|:------------------------:|
| Best   |      O(nlogn)       |
| Worst |      O(nlogn)       |
| Average |      O(nlogn)       |

## Radix Sort

Unlike the previous algorithms, a sorting algorithm that performs without comparisons. It sorts based on digits, so the digits must be able to be sorted lexicographically.

A type of bucket sort.

Not In-Place. Stable

### Time Complexity

Let n be the number of elements to be sorted, d be the maximum number of digits, and k be the number of buckets (for numbers, it is 10 as the digits are 0 to 9).

Both best, worst, and average cases have a complexity of O(d(n + k)).