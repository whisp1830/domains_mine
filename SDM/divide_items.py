

def divide_items(items,threads_num=20):

    if threads_num<=len(items):
        trader = len(items) // threads_num
        remainder = len(items) % threads_num
        A = items[:trader * threads_num]
        if remainder != 0:
            B = items[trader * threads_num:]
        else:
            B = []
        index = 0
        results = []
        while index < trader * threads_num:
            results.append(A[index:index + trader])
            index = index + trader
        results[-1].extend(B)
    else:
        results = [item for item in items]

    return results,len(results)

if __name__=="__main__":
    print divide_items(range(10))