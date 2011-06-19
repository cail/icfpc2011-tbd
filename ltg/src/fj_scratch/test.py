from timeit import timeit

print timeit('None.__str__')
print timeit('getattr(None, "__str__", None)')

