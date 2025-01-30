import functools
import sys
import traceback


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
            # print(f"=========> Excepción atrapada en {func.__name__}: {err}")
            class_name = self.__class__.__name__
            func_name = func.__name__
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
            last_tb = tb_lines[-2] if tb_lines else 'No traceback available'

            err_obj = {
                "class_error": class_name,
                "type_error": func_name,
                "error": str(err),
                "excepciones": err,
                "traceback": f"{last_tb}"
                # "error_message": type(err).__name__,
                # "err_message": err,
            }
            self.errors = err_obj
            # pass
    return wrapper
