import sys
import types
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
            return rng.rand(384)

    fake_mod.SentenceTransformer = FakeModel
    sys.modules['sentence_transformers'] = fake_mod

# Now import the MemoryModule
from backend.memory.memory_module import MemoryModule


def run_quick_test():
    print('Creating MemoryModule with fake model...')
    mm = MemoryModule(model='fake') if False else MemoryModule(model=FakeModel())

    print('Storing memories...')
    mm.store_memory('story_context', 'Once upon a time, in a magical forest...', {'agent': 'test'})
    mm.store_memory('story_context', 'A lonely knight wandered the valley.', {'agent': 'test'})
    mm.store_memory('character_descriptions', 'Elda, a curious young wizard with a wooden staff.', {'agent': 'character_agent'})

    print('Memory summary:', mm.get_memory_summary())

    print('Querying similar to "magical forest"...')
    results = mm.recall_similar('story_context', 'a magical forest', top_k=2)
    for r in results:
        print('-', r['content'][:80], '... sim=', r['similarity'])

    print('Recording feedback...')
    mm.record_feedback('StoryDirector', 0.92, 'Nice pacing and structure')

    print('Learning stats (before updates):', mm.get_learning_stats())
    mm.update_learning_pattern('story_coherence', 0.9)
    mm.update_learning_pattern('user_satisfaction', 0.8)
    print('Learning stats (after updates):', mm.get_learning_stats())

    print('Clearing memories...')
    mm.clear_memory('story_context')
    print('Memory summary after clear:', mm.get_memory_summary())


if __name__ == '__main__':
    run_quick_test()
