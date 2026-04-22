/* Batch 03: Array operations — uses pointer+length pairs, modeled as Array in Lean */

int sum_array(const int *arr, int n) {
    int s = 0;
    for (int i = 0; i < n; i++) {
        s += arr[i];
    }
    return s;
}

int product_array(const int *arr, int n) {
    int p = 1;
    for (int i = 0; i < n; i++) {
        p *= arr[i];
    }
    return p;
}

int max_element(const int *arr, int n) {
    int m = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] > m) m = arr[i];
    }
    return m;
}

int min_element(const int *arr, int n) {
    int m = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] < m) m = arr[i];
    }
    return m;
}

void reverse_array(int *arr, int n) {
    for (int i = 0; i < n / 2; i++) {
        int tmp = arr[i];
        arr[i] = arr[n - 1 - i];
        arr[n - 1 - i] = tmp;
    }
}

int is_sorted(const int *arr, int n) {
    for (int i = 0; i < n - 1; i++) {
        if (arr[i] > arr[i + 1]) return 0;
    }
    return 1;
}

int count_occurrences(const int *arr, int n, int val) {
    int c = 0;
    for (int i = 0; i < n; i++) {
        if (arr[i] == val) c++;
    }
    return c;
}
