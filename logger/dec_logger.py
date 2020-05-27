import datetime as dt


def param_logger(path):
    def logger(function):
        _LOGS = {}

        def do_log(*args, **kwargs):
            if _LOGS.get(function):
                pass
            else:
                _LOGS[function] = {}
            key = f'{str(args)}-{str(kwargs)}'
            result_data = _LOGS[function].get(key)
            if result_data is None:
                result = function(*args, **kwargs)
                result_data = {'date and time': dt.datetime.utcnow(),
                               'function name': function.__name__,
                               'arguments': [args, kwargs],
                               'what returned': result}
            with open(path, 'a') as f:
                f.write('------------\n')
                for key, value in result_data.items():
                    f.write(f'{key} - {value}\n')
            return result

        return do_log

    return logger
