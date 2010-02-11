from types import FunctionType, ClassType, InstanceType, MethodType
from sandbox import SandboxError
from .guard import guard

builtin_function_or_method = type(len)

SAFE_TYPES = (
    type(None), bool,
    int, long, 
    str, unicode, 
    builtin_function_or_method, FunctionType, 
)

def createObjectProxy(obj, SandboxError=SandboxError,
isinstance=isinstance, MethodType=MethodType):
    obj_class = obj.__class__
    obj_class_doc = proxy(obj_class.__doc__)

    class ObjectProxy:
        __doc__ = obj_class_doc 

        def __getattr__(self, name):
            value = getattr(obj, name)
            if isinstance(value, MethodType):
                value = MethodType(value.im_func, self, self.__class__)
            else:
                value = proxy(value)
            return value

        def __setattr__(self, name, value):
            raise SandboxError("Read only object proxy")

    for attr in ("__name__", "__module__"):
        value = getattr(obj_class, attr)
        value = proxy(value)
        setattr(ObjectProxy, attr, value)

    return ObjectProxy()

def _proxy(safe_types=SAFE_TYPES, file=file,
ClassType=ClassType, InstanceType=InstanceType, TypeError=TypeError):
    def proxy(value):
        if isinstance(value, safe_types):
            # Safe type, no need to create a proxy
            return value
        elif isinstance(value, tuple):
            return tuple(
                proxy(item)
                for item in value)
        elif isinstance(value, list):
            return list(
                proxy(item)
                for item in value)
        elif isinstance(value, dict):
            return dict(
                (proxy(key), proxy(value))
                for key, value in value.iteritems())
        elif isinstance(value, (file, ClassType, InstanceType)):
            return createObjectProxy(value)
        else:
            raise TypeError("Unable to proxy a value of type %s" % type(value))
    return proxy

proxy = _proxy()
del _proxy
