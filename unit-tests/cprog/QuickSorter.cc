#include "QuickSorter.h"

static void swap(std::vector<int>& list, int i, int k) {
    int v = list[i];
    list[i] = list[k];
    list[k] = v;
}

static int partition(std::vector<int>& list, int i, int k) {
    int pivot_value = list[k];
    int pivot_index = k - 1;
    
    for(int index = i; index < k; index++) {
        while((index < pivot_index) && (list[index] >= pivot_value)) {
            swap(list, index, pivot_index);
            pivot_index--;
        }
        while((index >= pivot_index) && (list[index] < pivot_value)) {
            swap(list, index, pivot_index);
            pivot_index++;
        }
    }
    swap(list, pivot_index, k);
    return pivot_index;
}

static void quicksort(std::vector<int>& list, int i, int k) {
    if(i < k) {
        int p = partition(list, i, k);
        quicksort(list, i, p-1);
        quicksort(list, p+1, k);
    }
}

QuickSorter::QuickSorter() {
    this->name = std::string("quicksort");
}

QuickSorter::~QuickSorter() {
}

void QuickSorter::sort(std::vector<int>& list) const {
    quicksort(list, 0, list.size()-1);
}
