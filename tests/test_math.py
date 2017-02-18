class TestMath:

    def setup_class(self):
        print("\n=== TestMath - setup class ===\n")

    def teardown_class(self):
        print("\n=== TestMath - teardown class ===\n")

    def setup(self):
        print("TestMath - setup method")

    def teardown(self):
        print("TestMath - teardown method")

    def test_add(self):
        assert(2 + 2 == 4)

    def test_mul(self):
        assert(3 * 3 == 9)