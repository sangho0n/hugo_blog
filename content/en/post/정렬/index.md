---
title: "Summary of Sorting Algorithms"
date: 2024-02-26T11:49:35+09:00
image: img/algorithm.png
tags: ["Technical Interview", "Algorithms", "sort", "cs", "interview"]
categories: ["Algorithms"]
---

Sorting algorithms should be chosen based on criteria such as time complexity in the best, average, and worst cases, as well as memory usage and stability.

The speed of sorting algorithms based on comparisons cannot be faster than ```O(nlog(n))``` in the worst case.

# List of Sorting Algorithms Covered in this Post

- Selection Sort
- Insertion Sort
- Bubble Sort
- Heap Sort
- Quick Sort
- Merge Sort
- Radix Sort

## Selection Sort

One of the simplest algorithms. Since it is an in-place algorithm, it is suitable for environments where copying operations are very slow.

At each step, the array is scanned once, selecting the minimum (maximum) value among the unsorted elements and swapping it with the front element.

After each step, the number of unsorted elements is reduced by one, and the same operation is repeated for the reduced array.

In-Place. Unstable.

### Time Complexity
| Case | Complexity |
|:----:|:--------:|
| Best | O(n^2)   |
| Worst | O(n^2) |
| Average | O(n^2) |

## Insertion Sort

Divides one array into a sorted array and an unsorted array, increasing the size of the sorted array step by step and decreasing the size of the unsorted array.

An unsorted array's front element is compared sequentially with the elements of the sorted array and inserted at the appropriate position.

In-Place. Stable.

### Time Complexity
| Case | Complexity |
|:----:|:--------:|
| Best (Already sorted) | O(n) |
| Worst | O(n^2) |
| Average | O(n^2) |

## Bubble Sort

At each step, the array is linearly searched, comparing adjacent elements and performing swap operations.

In-place. Stable.

### Time Complexity
| Case | Complexity |
|:----:|:--------:|
| Best | O(n^2) |
| Worst | O(n^2) |
| Average | O(n^2) |

## Heap Sort

A method of sorting using a max heap or min heap. It is possible to use a separate heap or make the given array a heap (In-place).

The operations of inserting/deleting elements in the heap are O(logn) (height of the heap), and these operations are repeated for the number of elements (twice; making a Heap + pulling elements one by one), so the total time complexity is O(nlogn).

In-Place. Unstable.

### Time Complexity
| Case | Complexity |
|:----:|:--------:|
| Best | O(nlogn) |
| Worst | O(nlogn) |
| Average | O(nlogn) |

## Quick Sort

Divides the array based on the pivot value into smaller values on the left and larger values on the right.

For each divided array, Quick Sort is performed iteratively until it cannot be divided further.

If the pivot is optimally selected at every moment, the given array is precisely divided in half every time. The worst case occurs when the pivot is consistently selected as the minimum (or maximum) value.

In-Place. Unstable.

### Time Complexity
| Case | Complexity |
|:----:|:--------:|
| Best | O(nlogn) |
| Worst | O(n^2) |
| Average | O(nlogn) |

## Merge Sort

One of the divide and conquer algorithms. The array is divided in half, and Merge Sort is performed on each divided array. Then, the sorted arrays are merged to obtain one large sorted array.

Unlike other sorting algorithms, it has O(n) level of space complexity even in the best case.

For the purpose of optimizing the divided array, you can mix Merge Sort with another sorting algorithm (such as Insertion Sort) that is not Merge Sort (this may result in instability).

not In-Place. Stable.

### Time Complexity
| Case | Complexity |
|:----:|:--------:|
| Best | O(nlogn) |
| Worst | O(nlogn) |
| Average | O(nlogn) |

## Radix Sort

Unlike the previous algorithms, a sorting algorithm that operates without comparisons. Since the numbers are sorted based on digits, the digits must be sortable in lexicographical order.

A kind of bucket sort.

not In-Place. Stable

### Time Complexity

Let n be the number of digits to be sorted, d be the maximum number of digits, and k be the number of buckets (0~9 for numbers).

Best, worst, and average cases are all O(d(n + k))
