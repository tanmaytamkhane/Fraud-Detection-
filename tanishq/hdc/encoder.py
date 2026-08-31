"""
HDC (Hyperdimensional Computing) Encoder for Fraud Detection.
Encodes 6 fraud signals into hypervectors using HDC.
"""
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import HDC_DIMENSIONS, HDC_NUM_LEVELS, HDC_SEED, NUM_SIGNALS, SIGNAL_NAMES

class HDCEncoder:
    def __init__(self, dim=HDC_DIMENSIONS, num_levels=HDC_NUM_LEVELS, num_signals=NUM_SIGNALS, seed=HDC_SEED):
        self.dim = dim
        self.num_levels = num_levels
        self.num_signals = num_signals
        self.rng = np.random.RandomState(seed)
        
        # Generate random base hypervectors
        # 1. Signal ID vectors: one per signal (6 vectors of dim=10000)
        #    These are bipolar: random +1/-1
        self.signal_hvs = self._generate_signal_hvs()
        
        # 2. Level vectors: quantized value representation  
        #    Use circular interpolation from two random endpoints
        self.level_hvs = self._generate_level_hvs()
    
    def _generate_signal_hvs(self):
        """Generate one random bipolar hypervector per signal."""
        # Shape: (num_signals, dim)
        hvs = self.rng.choice([-1, 1], size=(self.num_signals, self.dim))
        return hvs.astype(np.float32)
    
    def _generate_level_hvs(self):
        """Generate level hypervectors using circular interpolation.
        Level 0 and Level N are random. Intermediate levels are created
        by progressively flipping bits from level 0 toward level N.
        This ensures nearby levels have similar vectors (preserving similarity).
        """
        level_0 = self.rng.choice([-1, 1], size=self.dim).astype(np.float32)
        level_n = self.rng.choice([-1, 1], size=self.dim).astype(np.float32)
        
        # Find positions where level_0 and level_n differ
        diff_positions = np.where(level_0 != level_n)[0]
        num_diffs = len(diff_positions)
        self.rng.shuffle(diff_positions)
        
        levels = np.zeros((self.num_levels, self.dim), dtype=np.float32)
        levels[0] = level_0.copy()
        
        for i in range(1, self.num_levels):
            levels[i] = levels[i-1].copy()
            # How many bits to flip for this level
            start_idx = int((i - 1) * num_diffs / (self.num_levels - 1))
            end_idx = int(i * num_diffs / (self.num_levels - 1))
            flip_positions = diff_positions[start_idx:end_idx]
            levels[i][flip_positions] = level_n[flip_positions]
        
        return levels
    
    def _quantize(self, value):
        """Map a float in [0, 1] to a level index in [0, num_levels-1]."""
        value = np.clip(value, 0.0, 1.0)
        level = int(value * (self.num_levels - 1))
        return min(level, self.num_levels - 1)
    
    def encode_single(self, signal_values):
        """Encode one transaction's 6 signal values into a single hypervector.
        
        Args:
            signal_values: array of shape (num_signals,) with values in [0, 1]
        
        Returns:
            Hypervector of shape (dim,)
        
        Process:
        1. For each signal i:
           a. Quantize value to a level index
           b. Get the level hypervector for that value
           c. BIND (element-wise multiply) with signal_i's ID vector
        2. BUNDLE (element-wise add) all bound vectors
        3. Apply bipolar sign function (clip to +1/-1)
        """
        bundled = np.zeros(self.dim, dtype=np.float32)
        
        for i in range(self.num_signals):
            level_idx = self._quantize(signal_values[i])
            level_hv = self.level_hvs[level_idx]
            signal_hv = self.signal_hvs[i]
            # BIND: element-wise multiply
            bound = signal_hv * level_hv
            # BUNDLE: element-wise add
            bundled += bound
        
        # Bipolarize
        result = np.sign(bundled)
        result[result == 0] = 1  # tie-break
        return result
    
    def encode_batch(self, signal_matrix):
        """Encode a batch of transactions.
        
        Args:
            signal_matrix: numpy array of shape (n_samples, num_signals)
                          Each row is one transaction's 6 signal values in [0, 1]
        
        Returns:
            Hypervector matrix of shape (n_samples, dim)
        """
        n_samples = signal_matrix.shape[0]
        result = np.zeros((n_samples, self.dim), dtype=np.float32)
        
        for i in range(n_samples):
            result[i] = self.encode_single(signal_matrix[i])
        
        return result

if __name__ == '__main__':
    print("Testing HDC Encoder...")
    encoder = HDCEncoder(dim=1000, num_levels=100, num_signals=6, seed=42)
    # Generate 5 random transactions
    test_signals = np.random.rand(5, 6)
    encoded = encoder.encode_batch(test_signals)
    print(f"Original shape: {test_signals.shape}")
    print(f"Encoded shape: {encoded.shape}")
    # Compute similarities between the first and the rest
    from numpy.linalg import norm
    h0 = encoded[0]
    for i in range(1, 5):
        hi = encoded[i]
        sim = np.dot(h0, hi) / (norm(h0) * norm(hi))
        print(f"Cosine similarity between tx 0 and tx {i}: {sim:.4f}")
