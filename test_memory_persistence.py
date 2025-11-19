import sys
import types
import os
import tempfile
import numpy as np

# Create a fake sentence_transformers module if not installed
if 'sentence_transformers' not in sys.modules:
    fake_mod = types.SimpleNamespace()

    class FakeModel:
        def __init__(self, model_name=None):
            self.model_name = model_name

        def encode(self, texts, convert_to_numpy=True):
            # Return deterministic embedding based on hash for reproducibility
            if isinstance(texts, (list, tuple)):
                texts = texts[0]
            h = abs(hash(str(texts))) % (10**8)
            rng = np.random.RandomState(h)
            return rng.rand(128)

    fake_mod.SentenceTransformer = FakeModel
    sys.modules['sentence_transformers'] = fake_mod

from backend.memory.memory_module import MemoryModule


def run_persistence_test():
    tmp_db = os.path.join(tempfile.gettempdir(), "sw_memory_test.db")
    if os.path.exists(tmp_db):
        os.remove(tmp_db)

    print('Creating MemoryModule with persistence...')
    mm = MemoryModule(model=FakeModel(), persist=True, db_path=tmp_db)

    print('Storing memories...')
    mm.store_memory('story_context', 'A persistent tale of two cities.', {'agent': 'test'})
    mm.store_memory('character_descriptions', 'Mira, a brave explorer.', {'agent': 'char'})

    print('Memory summary after store:', mm.get_memory_summary())
    mm.close()

    print('Re-loading MemoryModule from DB...')
    mm2 = MemoryModule(model=FakeModel(), persist=True, db_path=tmp_db)
    print('Memory summary after reload:', mm2.get_memory_summary())

    # Clean up
    mm2.clear_memory()
    mm2.close()
    if os.path.exists(tmp_db):
        os.remove(tmp_db)


if __name__ == '__main__':
    run_persistence_test()
