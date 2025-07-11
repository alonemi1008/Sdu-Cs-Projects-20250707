pragma circom 2.0.0;

include "./poseidon2_components.circom";

// Main Poseidon2 hash function
// Parameters: (n=256, t=3, d=5)
// Input: 2 field elements (since t=3, one slot for capacity)
// Output: 1 field element (hash output)
template Poseidon2Hash() {
    signal input in[2];  // Two input elements
    signal output out;   // Single hash output
    
    // According to the paper, for t=3:
    // RF = 8 (full rounds)
    // RP = 56 (partial rounds) for 256-bit security
    var RF = 8;  // Number of full rounds
    var RP = 56; // Number of partial rounds
    var t = 3;   // State size
    
    // Initialize state: [in[0], in[1], 0] (capacity element is 0)
    signal state[RF + RP + 1][t];
    
    // Initial state
    state[0][0] <== in[0];
    state[0][1] <== in[1]; 
    state[0][2] <== 0;  // Capacity element
    
    component fullRounds[RF];
    component partialRounds[RP];
    
    // First RF/2 full rounds
    for (var i = 0; i < RF/2; i++) {
        fullRounds[i] = FullRound(i);
        fullRounds[i].in <== state[i];
        state[i+1] <== fullRounds[i].out;
    }
    
    // RP partial rounds
    for (var i = 0; i < RP; i++) {
        partialRounds[i] = PartialRound(RF/2 + i);
        partialRounds[i].in <== state[RF/2 + i];
        state[RF/2 + i + 1] <== partialRounds[i].out;
    }
    
    // Last RF/2 full rounds
    for (var i = RF/2; i < RF; i++) {
        fullRounds[i] = FullRound(RP + i);
        fullRounds[i].in <== state[RP + i];
        state[RP + i + 1] <== fullRounds[i].out;
    }
    
    // Output is the first element of final state
    out <== state[RF + RP][0];
}

// Poseidon2 hash for single block (wrapper)
template Poseidon2() {
    signal input in[2];
    signal output out;
    
    component hash = Poseidon2Hash();
    hash.in <== in;
    out <== hash.out;
} 