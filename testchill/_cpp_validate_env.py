import ast as _pyast
import itertools as _pyitertools
import random as _pyrandom
import types as _pytypes


_pylambdatype = _pycollections.namedtuple('LambdaType', ['paramtypes','exprtype'])
_pyarraytype = _pycollections.namedtuple('ArrayType', ['dimensions','basetype'])


class CppType(object):
    def __init__(self):
        pass


class CppPrimitiveType(CppType):
    _bycppname = {
            'char':                 ('char', 'c', 1, False, False, True, False),
            'signed char':          ('signed char', 'b', 1, True, False, False, False),
            'unsigned char':        ('unsigned char', 'B', 1, True, False, False, False),
            'short':                ('short', 'h', 2, True, False, False, True),
            'unsigned short':       ('unsigned short', 'H', 2, True, False, False, False),
            'int':                  ('int', 'i', 4, True, False, False, True),
            'unsigned int':         ('unsigned int', 'I', 4, True, False, False, False),
            'long':                 ('long', 'l', 4, True, False, False, True),
            'unsigned long':        ('unsigned long', 'L', 4, True, False, False, False),
            'long long':            ('long long', 'q', 8, True, False, False, True),
            'unsigned long long':   ('unsigned long long', 'Q', 8, True, False, False, False),
            'float':                ('float', 'f', 4, False, True, False, True),
            'double':               ('double', 'd', 8, False, True, False, True)
        }
    def __init__(self, cppname, structfmt, size, isint, isfloat, ischar, issigned):
        CppType.__init__(self)
        self.cppname = cppname
        self.size = size
        self.size_expr = 'sizeof(' + cppname + ')'
        self.structfmt = structfmt
        self.isint = isint
        self.isfloat = isfloat
        self.ischar = ischar
        self.issigned = issigned
    
    @staticmethod
    def get_from_cppname(cppname):
        return CppPrimitiveType(*CppPrimitiveType._bycppname[cppname])
    
    def getfreevars(self, glbls):
        return set()
    
    def getpytype(self):
        if self.ischar:
            return str
        elif self.isint:
            return int
        elif self.isfloat:
            return float


class CppArrayType(CppType):
    def __init__(self, basetype, dims=[None]):
        CppType.__init__(self)
        self.basetype = basetype
        self.dimensions = dims
    
    def getfreevars(self, glbls):
        return self.basetype.getfreevars(glbls) | set(d.getfreevars(glbls) for d in dimensions if hasattr(d, 'getfreevars'))


class CppPointerType(CppType):
    def __init__(self, basetype):
        CppType.__init__(self)
        self.basetype = basetype
    
    def getfreevars(self, glbls):
        return self.basetype.getfreevars(glbls)


class Parameter(object):
    def __init__(self, name, direction, cpptype, init_expr=None):
        self.name = name
        self.direction = direction
        self.cpptype = cpptype
        self.init_expr = init_expr
    
    @staticmethod
    def order_by_freevars(param_list, glbls):
        complete = set()
        stack = list((p.name, p, p.init_expr.getfreevars(glbls) | p.cpptype.getfreevars(glbls)))
        param_dict = dict((p[0], p) for p in stack)
        while len(stack):
            name, param, freevars = stack[0]
            stack = stack[1:]
            if name in complete:
                continue
            freevars = set(var for var in freevars if var not in complete)
            if not len(freevars):
                complete.add(name)
                yield param
            else:
                stack = [(name, param, freevars)] + stack
                for var in freevars:
                    stack = [param_dict[var]]


class Procedure(object):
    def __init__(self, name, rtype, parameters, global_dict):
        self.name = name
        self.rtype = rtype
        self.global_dict = global_dict
        self.parameters = list(Parameters.order_by_freevars(parameters, global_dict))
    
    def generatecode(self, codeprinter, istream_name, ostream_name):
        #TODO:
        pass
        

class _Expr(object):
    def __init__(self):
        pass
    
    def getfreevars(self, glbls):
        raise NotImplementedError
    
    def compile_to_lambda(self, glbls, target_type):
        args = _pyast.arguments(list(_pyast.Name(n, _pyast.Param()) for n in self.getfreevars(self, glbls)), None, None, [])
        expr = _pyast.Expression(_pyast.Lambda(args, self.compile_expr(target_type)))
        expr = _pyast.fix_missing_locations(expr)
        return eval(compile(expr, '<string>', 'eval'))


class _ConstantExpr(_Expr):
    def __init__(self, value):
        self.value = value
    
    def compile_expr(self, target_type):
        if target_type is None:
            return _pyast.parse(self.value, '<string>', 'eval').body
        elif target_type == chr:
            return _pyast.Str(chr(self.value))
        elif target_type == int:
            return _pyast.Num(int(self.value))
        elif target_type == str:
            return _pyast.Str(str(self.value))
        elif target_type == float:
            return _pyast.Num(float(self.value))


class _NameExpr(_Expr):
    def __init__(self, name):
        self.name = name
    
    def compile_expr(self, target_type):
        return _pyast.Name(self.name, _pyast.Load())
    
    def getfreevars(self, glbls):
        if self.name not in glbls:
            return set([self.name])
        else:
            return set()


class _AttributeExpr(_Expr):
    def __init__(self, expr, name):
        self.expr = expr
        self.name = name
    
    def compile_expr(self, target_type):
        return _pyast.Attribute(
            self.expr.compile_expr(None),
            self.name,
            _pyast.Load())
    
    def getfreevars(self, glbls):
        return self.expr.getfreevars(glbls)


class _BinExpr(_Expr):
    _optypes = {
            '+':  _pyast.Add,
            '-':  _pyast.Sub,
            '*':  _pyast.Mult,
            '**': _pyast.Pow,
            '/':  _pyast.Div
        }
    def __init__(self, left, op, right):
        self.left = left
        self.right = right
        self.op = op
    
    def compile_expr(self, target_type):
        return _pyast.BinOp(
                self.left.compile_expr(target_type),
                _BinExpr._optypes[self.op](),
                self.right.compile_expr(target_type))
    
    def getfreevars(self, glbls):
        return self.left.getfreevars(glbls) | self.right.getfreevars(glbls)


class _UnaryExpr(_Expr):
    _optypes = {
            '-': _pyast.USub
        }
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
    
    def compile_expr(self, target_type):
        return _pyast.UnaryOp(
                _UnaryExpr._optypes[self.op](),
                self.expr.compile_expr(target_type))
    
    def getfreevars(self, glbls):
        return self.expr.getfreevars(glbls)


class _LambdaExpr(_Expr):
    def __init__(self, params, expr):
        self.params = params
        self.expr = expr
    
    def compile_expr(self, target_type):
        assert isinstance(target_type, _pylambdatype)
        return _pyast.Lambda(
            _pyast.arguments([_pyast.Name(p, _pyast.Param()) for p in self.params], None, None, []),
            self.expr.compile_expr(target_type.exprtype))
    
    def getfreevars(self, glbls):
        new_glbls = set(glbls)
        new_glbls = new_glbls | set(self.params)
        return self.expr.getfreevars(new_glbls)


class _InvokeExpr(_Expr):
    def __init__(self, func, parameters):
        self.func = func
        self.parameters = parameters
    
    def compile_expr(self, target_type):
        lt = _pylambdatype([None for p in self.parameters], target_type)
        return _pyast.Call(
                self.func.compile_expr(_pylambdatype),
                [p.compile_expr(None) for p in self.parameters],
                [],
                None,
                None)


class _Generator(_Expr):
    def __init__(self):
        _Expr.__init__(self)
    
    
class _MatrixGenerator(_Generator):
    def __init__(self, dims, genexpr):
        self.dimensions = dims
        self.genexpr = genexpr
    
    def _compile_dims(self, target_type):
        dim_exprs = dict()
        assert isinstance(target_type, _pyarraytype)
        assert len(target_type.dimensions) == len(self.dimensions)
        for i, d in enumerate(target_type.dimensions):
            if d is None:
                d = self.dimensions[i]
            dim_epxrs[i] = d.compile_expr(....)
        return dim_exprs
    
    def compile_expr(self, target_type):
        dims = self._compile_dims(target_type)
        
        #def array(func,dims):
        #    return [tuple(d, func(*d)) for d in itertools.product(*(map(range,dims))]
        ltype = _pylambdatype([int for d in target_type.dimensions], target_type.basetype)
        elt_expr = _pyast.Call(self.genexpr.compile_expr(ltype), [], [], _pyast.Name('_d', _pyast.Load()), None)                  # func(*d)
        elt_expr = _pyast.Call(_pyast.Name('tuple', _pyast.Load()), [_pyast.Name('_d', _pyast.Load()), elt_expr], [], None, None) # tuple(d, func(*d))
        pdt_expr = _pyast.Attribute(_pyast.Name('itertools', _pyast.Load()), 'product', _pyast.Load())                            # itertools.product
        itr_expr = _pyast.Call(_pyast.Name('map', _pyast.Load()), [_pyast.Name('range', _pyast.Load()), dims], [], None, None)    # map(range,dims)
        itr_expr = _pyast.Call(pdt_expr, [], [], itr_expr, None)                                                                  # itertools.product(*(map(range,dims)))
        return _pyast.ListComp(
            elt_expr,
            [_pyast.comprehension(_pyast.Name('_d', _pyast.Store()), itr_expr, [])])
    
    def getfreevars(self, glbls):
        return self.genexpr.getfreevars(glbls)


class _RandomExpr(_Expr):
    def __init__(self, self.minexpr, self.maxexpr):
        self.expr = _BinExpr(
            _BinExpr(
                _InvokeExpr(_AttributeExpr(_NameExpr('random'),'random'),[]),
                '*'
                _BinExpr(self.maxexpr, '-', self.minexpr)),
            '+',
            self.minexpr)
    
    def getfreevars(self, glbls):
        return self.minexpr.getfreevars(glbls) | self.maxexpr.getfreevars(glbls)
    
    def compile_expr(self, target_type):
        return self.expr.compile_expr(target_type)
        
        
        
