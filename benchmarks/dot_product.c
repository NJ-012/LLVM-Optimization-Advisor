#include <stdio.h>
#define N 1600000
static double a[N],b[N];
int main(void){for(int i=0;i<N;i++){a[i]=(i%31)*0.1;b[i]=(i%23)*0.2;}double s=0;for(int i=0;i<N;i++)s+=a[i]*b[i];printf("%.8f\n",s);return 0;}
