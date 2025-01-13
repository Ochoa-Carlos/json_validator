import functools

def wrapper_handler(func):
    """Error handler."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs) -> None:
        if hasattr(self, "_executed_functions") and func.__name__ in self.executed_functions:
            return
        try:
            result = func(self, *args, **kwargs)
            self.executed_functions.add(func.__name__)
            return result
        except Exception as err:
            print(f"Excepción atrapada en {func.__name__}: {err}")
            self.executed_functions.add(func.__name__)
            self.error[func.__name__] = err
            self.errors.append(err)
            return None
    return wrapper
