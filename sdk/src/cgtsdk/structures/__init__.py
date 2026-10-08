"""Reference structures, each with an operational grammar (Structure.grammar())."""
from .associative import HashTableStructure, HeapStructure, TrieStructure, stable_hash
from .graphs import AutomatonStructure, GraphStructure
from .sequences import (ArrayStructure, DequeStructure, LinkedListStructure,
                        QueueStructure, StackStructure)
from .trees import BinaryTreeStructure, BSTStructure

ALL = (ArrayStructure, LinkedListStructure, StackStructure, QueueStructure, DequeStructure,
       HashTableStructure, HeapStructure, TrieStructure, BinaryTreeStructure, BSTStructure,
       GraphStructure, AutomatonStructure)

__all__ = [c.__name__ for c in ALL] + ["stable_hash", "ALL"]
