#include "MergeSorter.h"

static void mergesort(std::vector<int>& lst, int start, int end) {
    if(start == end) return;
    int center = start + (end-start)/2;
    mergesort(lst, start, center);
    mergesort(lst, center+1, end);
    std::vector<int> left = std::vector<int>(lst.begin()+start, lst.begin()+(center+1));
    std::vector<int> right = std::vector<int>(lst.begin()+(center+1),lst.begin()+(end+1));
    int i = 0;
    int j = 0;
    for(int k = start; k < (end+1); k++) {
        if (i >= left.size()) {
            lst[k] = right[j++];
        }
        else if(j >= right.size()) {
            lst[k] = left[i++];
        }
        else if(left[i] > right[j]) {
            lst[k] = right[j++];
        }
        else {
            lst[k] = left[i++];
        }
    }
}

MergeSorter::MergeSorter() {
    this->name = std::string("mergesort");
}

MergeSorter::~MergeSorter() {
}

void MergeSorter::sort(std::vector<int>& list) const {
    mergesort(list, 0, list.size()-1);
}
