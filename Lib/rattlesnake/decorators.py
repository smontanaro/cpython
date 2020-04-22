"Decorators for debugging"

import opcode

def debug_method(meth):
    "display input args and returned result."
    def wrap(*args, **kwds):
        self = args[0]
        old_stack = str(getattr(self, "stacklevel", ""))
        result = meth(*args, **kwds)
        new_stack = str(getattr(self, "stacklevel", ""))
        args_str = f"{','.join(repr(arg) for arg in args[1:])}" if args else ""
        sep = ", " if args and kwds else ""
        kwds_str = f"**{kwds}" if kwds else ""
        name = meth.__name__
        klass = args[0].__class__.__name__
        if old_stack:
            print(f"! {klass}.{name}({args_str}{sep}{kwds_str}) -> {result}"
                  f" ({old_stack} -> {new_stack})")
        else:
            print(f"! {klass}.{name}({args_str}{sep}{kwds_str}) -> {result}")
        return result
    return wrap

def debug_convert(meth):
    "display input args and returned result."
    def wrap(*args, **kwds):
        self = args[0]
        old_stack = str(self.stacklevel)
        result = meth(*args, **kwds)
        new_stack = str(self.stacklevel)
        oldop = opcode.opname[args[1][0]]
        oldarg = args[1][1]
        name = meth.__name__
        klass = args[0].__class__.__name__
        res = []
        for (op, oparg) in result:
            res.append((opcode.opname[op], oparg))
        print(f"! {klass}.{name}(({oldop}, {oldarg})) -> {res}"
              f" ({old_stack} -> {new_stack})")
        return result
    return wrap

def debug_function(func):
    "display input args and returned result."
    def wrap(*args, **kwds):
        result = func(*args, **kwds)
        args_str = f"{','.join(repr(arg) for arg in args)}" if args else ""
        sep = ", " if args and kwds else ""
        kwds_str = f"**{kwds}" if kwds else ""
        print(f"! {func.__name__}({args_str}{sep}{kwds_str}) -> {result}")
        return result
    return wrap
