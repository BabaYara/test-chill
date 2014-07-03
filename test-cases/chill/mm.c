/*
    <test>
        import random
        an = 8 + int(random.next()*25)
        bm = 8 + int(random.next()*25)
        ambn = 8 + int(random.next()*25)
        TestProcedure(
            'void mm(float** A, float** B, float** C, int ambn, int an, int bm)',
            matrix(an,ambn,lambda i,j: 8 - random()*4),
            matrix(ambn,bm,lambda i,j: 8 - random()*4),
            out(),
            ambn,
            an,
            bm)
    </test>
    or
    <test>
        test void mm(
            in  float** A    = matrix(an, ambn, even_dist(8 - random()*4)),
            in  float** B    = matrix(ambn, bm, even_dist(8 - random()*4)),
            out float** C    = matrix(an,   bm, even_dist(0)),
            in  int     ambn = 8 + randint(0, 8),
            in  int     an   = 8 + randint(0, 8),
            in  int     bm   = 8 + randint(0, 8))
    </test>
 */

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

