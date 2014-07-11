#define AN 3
#define BM 2
#define AMBN 5

/*
<test name='mm_small'>

with {an:3, bm:2, ambn:5, evendist2:lambda i,j: random(-8,8), zero2=lambda i,j: 0}
procedure void mm(
    in  float[an][ambn] A = matrix([*,*],evendist2),
    in  float[ambn][bm] B = matrix([*,*],evendist2),
    out float[an][bm]   C = matrix([*,*],zero2))

</test>
*/

void mm(float A[AN][AMBN], float B[AMBN][BM], float C[AN][BM]) {
    int i;
    int j;
    int k;
    for(i = 0; i < AN; i++) {
        for(j = 0; j < BM; j++) {
            for(k = 0; k < AMBN; k++) {
                C[i][j] += A[i][k] + B[k][j];
            }
        }
    }
}
