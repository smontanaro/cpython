
from . import InstructionTest

class BinOpTest(InstructionTest):
    def test_add(self):
        def add(a, b):
            return a + b
        (pyvm, rvm) = self.function_helper(add)
        self.assertEqual(pyvm(5, 70), rvm(5, 70))
        self.assertEqual(pyvm("xyz", "abc"), rvm("xyz", "abc"))

    def test_and(self):
        def and_(a, b):
            return a & b
        (pyvm, rvm) = self.function_helper(and_)
        self.assertEqual(pyvm(5, 70), rvm(5, 70))

    def test_is(self):
        def is_(a, b):
            return a is b
        (pyvm, rvm) = self.function_helper(is_)
        self.assertEqual(pyvm(5, 70), rvm(5, 70))
        self.assertEqual(pyvm(None, None), rvm(None, None))

    def test_is_not(self):
        def is_not(a, b):
            return a is not b
        (pyvm, rvm) = self.function_helper(is_not)
        self.assertEqual(pyvm(5, 70), rvm(5, 70))
        self.assertEqual(pyvm(None, None), rvm(None, None))

    def test_floor_divide(self):
        def floor_divide(a, b):
            return a // b
        (pyvm, rvm) = self.function_helper(floor_divide)
        self.assertEqual(pyvm(1, 5), rvm(1, 5))
        self.assertEqual(pyvm(5, 1), rvm(5, 1))

    def test_inplace_add(self):
        def inplace_add(a, b):
            a += b
            return a
        (pyvm, rvm) = self.function_helper(inplace_add)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))

    def test_inplace_and(self):
        def inplace_and(a, b):
            a &= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_and)
        self.assertEqual(pyvm(5, 99), rvm(5, 99))

    def test_inplace_floor_divide(self):
        def inplace_floor_divide(a, b):
            a //= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_floor_divide)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))
        self.assertEqual(pyvm(9, 5), rvm(9, 5))

    def test_inplace_lshift(self):
        def inplace_lshift(a, b):
            a <<= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_lshift)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))

    def test_inplace_mod(self):
        def inplace_mod(a, b):
            a %= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_mod)
        self.assertEqual(pyvm(15, 9), rvm(15, 9))

    def test_inplace_mul(self):
        def inplace_mul(a, b):
            a *= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_mul)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))

    def test_inplace_or(self):
        def inplace_or(a, b):
            a |= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_or)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))

    def test_inplace_pow(self):
        def inplace_pow(a, b):
            a **= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_pow)
        self.assertEqual(pyvm(5, 9.1), rvm(5, 9.1))

    def test_inplace_rshift(self):
        def inplace_rshift(a, b):
            a >>= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_rshift)
        self.assertEqual(pyvm(5 ** 9, 4), rvm(5 ** 9, 4))

    def test_inplace_subtract(self):
        def inplace_subtract(a, b):
            a -= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_subtract)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))

    def test_inplace_true_divide(self):
        def inplace_true_divide(a, b):
            a /= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_true_divide)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))
        self.assertEqual(pyvm(9.0, 4), rvm(9.0, 4))

    def test_inplace_xor(self):
        def inplace_xor(a, b):
            a ^= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_xor)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))

    def test_invert(self):
        def invert(val):
            return ~val
        (pyvm, rvm) = self.function_helper(invert)
        for val in (5, -99):
            self.assertEqual(pyvm(val), rvm(val))

    def test_lshift(self):
        def lshift(a, b):
            return a << b
        (pyvm, rvm) = self.function_helper(lshift)
        self.assertEqual(pyvm(70, 5), rvm(70, 5))

    def test_modulo(self):
        def modulo(a, b):
            return a % b
        (pyvm, rvm) = self.function_helper(modulo)
        self.assertEqual(pyvm(5, 2), rvm(5, 2))
        self.assertEqual(pyvm("%s", 47), rvm("%s", 47))

    def test_or(self):
        def or_(a, b):
            return a | b
        (pyvm, rvm) = self.function_helper(or_)
        self.assertEqual(pyvm(5, 70), rvm(5, 70))

    def test_power(self):
        def power(base, exp):
            return base ** exp
        (pyvm, rvm) = self.function_helper(power)
        self.assertEqual(pyvm(5.0, 7), rvm(5.0, 7))

    def test_product(self):
        def product(a, b):
            return a * b
        (pyvm, rvm) = self.function_helper(product)
        self.assertEqual(pyvm(1, 5), rvm(1, 5))
        self.assertEqual(pyvm(5, 1), rvm(5, 1))

    def test_rshift(self):
        def rshift(a, b):
            return a >> b
        (pyvm, rvm) = self.function_helper(rshift)
        self.assertEqual(pyvm(79999, 3), rvm(79999, 3))

    def test_subtract(self):
        def subtract(a, b):
            return a - b
        (pyvm, rvm) = self.function_helper(subtract)
        self.assertEqual(pyvm(5, 9.0), rvm(5, 9.0))

    def test_true_divide(self):
        def true_divide(a, b):
            return a / b
        (pyvm, rvm) = self.function_helper(true_divide)
        self.assertEqual(pyvm(1, 5), rvm(1, 5))
        self.assertEqual(pyvm(5, 1), rvm(5, 1))

    def test_xor(self):
        def xor(a, b):
            return a ^ b
        (pyvm, rvm) = self.function_helper(xor)
        self.assertEqual(pyvm(5, 70), rvm(5, 70))

    def test_matmul(self):
        def matmul(a, b):
            return a @ b
        mata = Matrix([[1, 2.0], [1.0, 3]])
        matb = Matrix([[10, 11], [-1.0, -3]])
        (pyvm, rvm) = self.function_helper(matmul)
        self.assertEqual(pyvm(mata, matb), rvm(mata, matb))

    def test_inplace_matmul(self):
        def inplace_matmul(a, b):
            a @= b
            return a
        a_list = [[1, 2.0], [1.0, 3]]
        b_list = [[10, 11], [-1.0, -3]]
        (pyvm, rvm) = self.function_helper(inplace_matmul)
        pyvm_result = pyvm(Matrix(a_list), Matrix(b_list))
        rvm_result = rvm(Matrix(a_list), Matrix(b_list))
        self.assertEqual(pyvm_result, rvm_result)

class Matrix:
    def __init__(self, mat):
        "Operate on mat - list of lists having dimension rows x cols"
        self.matrix = mat
        # Note that we make few assumptions about the structure of the
        # arrays. Since this is just for testing, I think that's okay.

    def __matmul__(self, other):
        "self @ other, return a new result Matrix"
        assert len(self.matrix[0]) == len(other.matrix)
        new_matrix = []
        for (i, row) in enumerate(self.matrix):
            new_matrix.append([])
            for j in range(len(self.matrix[0])):
                col = other.column(j)
                new_matrix[i].append(sum(e1 * e2 for (e1, e2) in
                                         zip(row, col)))
        return Matrix(new_matrix)

    def column(self, i):
        "extra column i as a list from matrix"
        result = []
        for row in self.matrix:
            result.append(row[i])
        return result

    def __eq__(self, other):
        return self.matrix == other.matrix
