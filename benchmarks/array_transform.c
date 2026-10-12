#include <stdio.h>
#define N 1300000
static double a[N],b[N];
int main(void){for(int i=0;i<N;i++)a[i]=(i%97)*0.02;for(int i=0;i<N;i++)b[i]=a[i]*a[i]+2.0*a[i]+1.0;double s=0;for(int i=0;i<N;i++)s+=b[i];printf("%.8f\n",s);return 0;}
