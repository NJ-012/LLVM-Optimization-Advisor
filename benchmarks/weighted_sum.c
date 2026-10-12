#include <stdio.h>
#define N 1200000
static float a[N];
int main(void){for(int i=0;i<N;i++)a[i]=(i%113)*0.03f;float s=0;for(int i=0;i<N;i++)s+=a[i]*(float)(i%7);printf("%.8f\n",s);return 0;}
