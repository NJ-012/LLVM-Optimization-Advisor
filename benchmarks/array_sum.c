#include <stdio.h>
#define N 1800000
static double a[N];
int main(void){ for(int i=0;i<N;i++) a[i]=(double)(i%97)*0.5; double s=0; for(int i=0;i<N;i++) s+=a[i]; printf("%.8f\n",s); return 0;}
