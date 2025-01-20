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
            # print(f"Excepción atrapada en {func.__name__}: {err}")
            self.executed_functions.add(func.__name__)
            self.errors[func.__name__] = err
            self.error.append(err)
            return None
    return wrapper


# TODO redistribuir y unir de ser posible ambos decoradores
def exception_wrapper(func):
    """Exception wrapper for internals classes ."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs) -> None:
        if hasattr(self, "_executed_functions") and func.__name__ in self.exc_funcs:
            pass
            # return
        try:
            result = func(self, *args, **kwargs)
            self.exc_funcs = func.__name__
            return result
        except Exception as err:
            # print(f"Excepción atrapada en {func.__name__}: {err}")
            err_obj = {
                "func_error": func.__name__,
                "error": str(err)
            }
            self.errors = err_obj
            return
    return wrapper
