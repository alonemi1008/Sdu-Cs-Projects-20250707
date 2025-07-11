pragma circom 2.0.0;

include "./poseidon2_hash.circom";

// Main circuit for Poseidon2 hash proof
// Public input: expected hash value
// Private input: preimage (original values)
// Proves knowledge of preimage that produces the given hash
template Poseidon2Proof() {
    // Private inputs (witness)
    signal input preimage[2];          // The secret values to be hashed
    
    // Public inputs  
    signal input expectedHash;         // The expected hash output
    
    // Compute hash of the preimage
    component hasher = Poseidon2();
    hasher.in[0] <== preimage[0];
    hasher.in[1] <== preimage[1];
    
    // Constraint: computed hash must equal expected hash
    expectedHash === hasher.out;
}

// Main component
component main {public [expectedHash]} = Poseidon2Proof(); 