#include <stdio.h>
#define N 170
static double a[N][N],b[N][N],c[N][N];
int main(void){ for(int i=0;i<N;i++)for(int j=0;j<N;j++){a[i][j]=(i+j)%17*0.1;b[i][j]=(i*3+j)%19*0.2;c[i][j]=0;} for(int i=0;i<N;i++)for(int k=0;k<N;k++)for(int j=0;j<N;j++)c[i][j]+=a[i][k]*b[k][j]; double checksum=0.0;for(int i=0;i<N;++i)for(int j=0;j<N;++j)checksum+=c[i][j]*(double)(1+i*N+j);printf("%.8f\n",checksum); return 0;}
