'''
Bubble sort Algorithm 
Returns a sorted copy of the dataset
DOES NOT SORT THE ORIGINAL DATASET

Arguments:
    dataset : the dataset to be copied and sorted
Returns:
    sorted copy of the dataset
'''
def bubble_sort(dataset):
    #Copy the original dataset to avoid editing the original values
    #   "dataset" contents should not be edited
    _output = dataset.copy()

    #Bubble sort swapping
    for i in range(0, len(_output)):
        for j in range(0, len(_output)-1-i):
            if _output[j] > _output[j+1]:
                _temp = _output[j]
                _output[j] = _output[j+1]
                _output[j+1] = _temp
    
    return _output


# inp = [2, "eight"]
# print(bubble_sort(inp))

