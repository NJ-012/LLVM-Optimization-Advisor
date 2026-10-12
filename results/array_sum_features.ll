; ModuleID = '/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/array_sum.c'
source_filename = "/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/array_sum.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@a = internal global [1800000 x double] zeroinitializer, align 16
@.str = private unnamed_addr constant [6 x i8] c"%.8f\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  %3 = alloca double, align 8
  %4 = alloca i32, align 4
  store i32 0, ptr %1, align 4
  store i32 0, ptr %2, align 4
  br label %5

5:                                                ; preds = %16, %0
  %6 = load i32, ptr %2, align 4
  %7 = icmp slt i32 %6, 1800000
  br i1 %7, label %8, label %19

8:                                                ; preds = %5
  %9 = load i32, ptr %2, align 4
  %10 = srem i32 %9, 97
  %11 = sitofp i32 %10 to double
  %12 = fmul double %11, 5.000000e-01
  %13 = load i32, ptr %2, align 4
  %14 = sext i32 %13 to i64
  %15 = getelementptr inbounds [1800000 x double], ptr @a, i64 0, i64 %14
  store double %12, ptr %15, align 8
  br label %16

16:                                               ; preds = %8
  %17 = load i32, ptr %2, align 4
  %18 = add nsw i32 %17, 1
  store i32 %18, ptr %2, align 4
  br label %5, !llvm.loop !6

19:                                               ; preds = %5
  store double 0.000000e+00, ptr %3, align 8
  store i32 0, ptr %4, align 4
  br label %20

20:                                               ; preds = %30, %19
  %21 = load i32, ptr %4, align 4
  %22 = icmp slt i32 %21, 1800000
  br i1 %22, label %23, label %33

23:                                               ; preds = %20
  %24 = load i32, ptr %4, align 4
  %25 = sext i32 %24 to i64
  %26 = getelementptr inbounds [1800000 x double], ptr @a, i64 0, i64 %25
  %27 = load double, ptr %26, align 8
  %28 = load double, ptr %3, align 8
  %29 = fadd double %28, %27
  store double %29, ptr %3, align 8
  br label %30

30:                                               ; preds = %23
  %31 = load i32, ptr %4, align 4
  %32 = add nsw i32 %31, 1
  store i32 %32, ptr %4, align 4
  br label %20, !llvm.loop !8

33:                                               ; preds = %20
  %34 = load double, ptr %3, align 8
  %35 = call i32 (ptr, ...) @printf(ptr noundef @.str, double noundef %34)
  ret i32 0
}

declare i32 @printf(ptr noundef, ...) #1

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"Ubuntu clang version 18.1.3 (1ubuntu1)"}
!6 = distinct !{!6, !7}
!7 = !{!"llvm.loop.mustprogress"}
!8 = distinct !{!8, !7}
