from memory_profiler import memory_usage


# @profile(stream=open("memory_profile.log", "w+"))
def my_func():
    a = [1] * (10**6)
    b = [2] * (2 * 10**7)
    del b
    return a


if __name__ == "__main__":

    mem_usage = memory_usage((my_func,))

    print(f"Memory usage over time: {mem_usage}")
    print(f"Peak memory usage: {max(mem_usage)} MiB")
