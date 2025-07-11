pragma circom 2.0.0;

// Poseidon2 Hash Algorithm Components
// Parameters: (n=256, t=3, d=5) - 256-bit field, 3 state elements, degree 5 S-box

// S-box component: x^5 for full rounds
template SBox() {
    signal input in;
    signal output out;
    
    signal x2 <== in * in;
    signal x4 <== x2 * x2;
    out <== x4 * in;
}

// Poseidon2 linear layer for t=3
// Using optimized matrix multiplication from the paper
template LinearLayer() {
    signal input in[3];
    signal output out[3];
    
    // Poseidon2 linear layer for t=3 (optimized)
    // Based on Table 1 parameters for (256,3,5)
    signal sum <== in[0] + in[1] + in[2];
    
    out[0] <== sum + 2 * in[0];
    out[1] <== sum + 2 * in[1]; 
    out[2] <== sum + 2 * in[2];
}

// Partial S-box for middle rounds (only first element)
template PartialSBox() {
    signal input in[3];
    signal output out[3];
    
    component sbox = SBox();
    sbox.in <== in[0];
    
    out[0] <== sbox.out;
    out[1] <== in[1];
    out[2] <== in[2];
}

// Full S-box for full rounds (all elements)
template FullSBox() {
    signal input in[3];
    signal output out[3];
    
    component sbox[3];
    for (var i = 0; i < 3; i++) {
        sbox[i] = SBox();
        sbox[i].in <== in[i];
        out[i] <== sbox[i].out;
    }
}

// Add round constants
template AddRoundConstants(round) {
    signal input in[3];
    signal output out[3];
    
    // Round constants for Poseidon2 with t=3
    // These should be generated using proper method from the paper
    var roundConstants[3];
    
    // Simplified constants for demonstration (should use proper generation)
    if (round == 0) {
        roundConstants = [
            0x0000000000000000000000000000000000000000000000000000000000000001,
            0x0000000000000000000000000000000000000000000000000000000000000002,
            0x0000000000000000000000000000000000000000000000000000000000000003
        ];
    } else if (round == 1) {
        roundConstants = [
            0x0000000000000000000000000000000000000000000000000000000000000004,
            0x0000000000000000000000000000000000000000000000000000000000000005,
            0x0000000000000000000000000000000000000000000000000000000000000006
        ];
    } else if (round == 2) {
        roundConstants = [
            0x0000000000000000000000000000000000000000000000000000000000000007,
            0x0000000000000000000000000000000000000000000000000000000000000008,
            0x0000000000000000000000000000000000000000000000000000000000000009
        ];
    } else if (round == 3) {
        roundConstants = [
            0x000000000000000000000000000000000000000000000000000000000000000a,
            0x000000000000000000000000000000000000000000000000000000000000000b,
            0x000000000000000000000000000000000000000000000000000000000000000c
        ];
    } else {
        roundConstants = [
            0x000000000000000000000000000000000000000000000000000000000000000d,
            0x000000000000000000000000000000000000000000000000000000000000000e,
            0x000000000000000000000000000000000000000000000000000000000000000f
        ];
    }
    
    for (var i = 0; i < 3; i++) {
        out[i] <== in[i] + roundConstants[i];
    }
}

// Single round for full rounds
template FullRound(round) {
    signal input in[3];
    signal output out[3];
    
    component addConstants = AddRoundConstants(round);
    component fullSBox = FullSBox();
    component linearLayer = LinearLayer();
    
    // Add round constants
    addConstants.in <== in;
    
    // Apply S-box to all elements
    fullSBox.in <== addConstants.out;
    
    // Apply linear layer
    linearLayer.in <== fullSBox.out;
    out <== linearLayer.out;
}

// Single round for partial rounds  
template PartialRound(round) {
    signal input in[3];
    signal output out[3];
    
    component addConstants = AddRoundConstants(round);
    component partialSBox = PartialSBox();
    component linearLayer = LinearLayer();
    
    // Add round constants
    addConstants.in <== in;
    
    // Apply S-box to first element only
    partialSBox.in <== addConstants.out;
    
    // Apply linear layer
    linearLayer.in <== partialSBox.out;
    out <== linearLayer.out;
} 