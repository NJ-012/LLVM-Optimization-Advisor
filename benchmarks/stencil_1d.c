#include <stdio.h>
#define N 500000
static double a[N],b[N];
int main(void){for(int i=0;i<N;i++)a[i]=(i%101)*0.01;for(int t=0;t<18;t++){b[0]=a[0];b[N-1]=a[N-1];for(int i=1;i<N-1;i++)b[i]=0.25*a[i-1]+0.5*a[i]+0.25*a[i+1];for(int i=0;i<N;i++)a[i]=b[i];}printf("%.8f\n",a[N/2]);return 0;}
