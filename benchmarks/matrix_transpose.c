#include <stdio.h>
#define N 700
static double a[N][N],b[N][N];
int main(void){for(int i=0;i<N;i++)for(int j=0;j<N;j++)a[i][j]=(i+j)%101*0.01;for(int i=0;i<N;i++)for(int j=0;j<N;j++)b[j][i]=a[i][j];double checksum=0.0;for(int i=0;i<N;++i)for(int j=0;j<N;++j)checksum+=b[i][j]*(double)(1+i*N+j);printf("%.8f\n",checksum);return 0;}
