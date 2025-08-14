class ExpressionNode:
    
    def __init__(self, value, left=None, right=None):
        self.value = value  # The operator ('+', '-', '*', '/') or operand ('agg1', 'agg2')
        self.left = left    # Left subtree
        self.right = right  # Right subtree

    def __repr__(self):
        if self.left is None and self.right is None:
            return str(self.value)
        return f"({self.left} {self.value} {self.right})"
