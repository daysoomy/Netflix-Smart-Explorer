# Algoritma Searching: Linear Search
def linear_search(data, key, target):
    results = []
    target = target.lower()
    for item in data:
        # Mencari teks di dalam kolom yang dipilih (title/cast/description)
        if target in str(item[key]).lower():
            results.append(item)
    return results

# Algoritma Sorting: Merge Sort
def merge_sort(data, key, reverse=False):
    if len(data) <= 1:
        return data
    
    mid = len(data) // 2
    left = merge_sort(data[:mid], key, reverse)
    right = merge_sort(data[mid:], key, reverse)
    
    return merge(left, right, key, reverse)

def merge(left, right, key, reverse):
    result = []
    while left and right:
        # Logika pembanding untuk string atau angka
        val_left = left[0][key]
        val_right = right[0][key]
        
        if not reverse:
            if val_left <= val_right: result.append(left.pop(0))
            else: result.append(right.pop(0))
        else:
            if val_left >= val_right: result.append(left.pop(0))
            else: result.append(right.pop(0))
                
    result.extend(left or right)
    return result