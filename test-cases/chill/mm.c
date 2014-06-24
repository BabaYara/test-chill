// test mm(A,B,C,AMBN,AN,BM)
// in int AMBN range(4,32)
// in int AN range(4,32)
// in int BM range(4,32)
// in float** A matrix(AN,AMBN,range(-5,5))
// in float** B matrix(AMBN,BM,range(-5,5))
// out float** C matrix(AN,BM)
// end test

void mm(float **A, float **B, float **C, int ambn, int an, int bm) {
  int i, j, n;

  for(i = 0; i < an; i++) {
    for(j = 0; j < bm; j++) {
      C[i][j] = 0.0f;
      for(n = 0; n < ambn; n++) {
        C[i][j] += A[i][n] * B[n][j];
      }
    }
  }
}

