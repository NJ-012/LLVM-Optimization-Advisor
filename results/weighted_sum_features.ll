; ModuleID = '/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/weighted_sum.c'
source_filename = "/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/weighted_sum.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@a = internal global [1200000 x float] zeroinitializer, align 16
@.str = private unnamed_addr constant [6 x i8] c"%.8f\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  %3 = alloca float, align 4
  %4 = alloca i32, align 4
  store i32 0, ptr %1, align 4
  store i32 0, ptr %2, align 4
  br label %5

5:                                                ; preds = %16, %0
  %6 = load i32, ptr %2, align 4
  %7 = icmp slt i32 %6, 1200000
  br i1 %7, label %8, label %19

8:                                                ; preds = %5
  %9 = load i32, ptr %2, align 4
  %10 = srem i32 %9, 113
  %11 = sitofp i32 %10 to float
  %12 = fmul float %11, 0x3F9EB851E0000000
  %13 = load i32, ptr %2, align 4
  %14 = sext i32 %13 to i64
  %15 = getelementptr inbounds [1200000 x float], ptr @a, i64 0, i64 %14
  store float %12, ptr %15, align 4
  br label %16

16:                                               ; preds = %8
  %17 = load i32, ptr %2, align 4
  %18 = add nsw i32 %17, 1
  store i32 %18, ptr %2, align 4
  br label %5, !llvm.loop !6

19:                                               ; preds = %5
  store float 0.000000e+00, ptr %3, align 4
  store i32 0, ptr %4, align 4
  br label %20

20:                                               ; preds = %33, %19
  %21 = load i32, ptr %4, align 4
  %22 = icmp slt i32 %21, 1200000
  br i1 %22, label %23, label %36

23:                                               ; preds = %20
  %24 = load i32, ptr %4, align 4
  %25 = sext i32 %24 to i64
  %26 = getelementptr inbounds [1200000 x float], ptr @a, i64 0, i64 %25
  %27 = load float, ptr %26, align 4
  %28 = load i32, ptr %4, align 4
  %29 = srem i32 %28, 7
  %30 = sitofp i32 %29 to float
  %31 = load float, ptr %3, align 4
  %32 = call float @llvm.fmuladd.f32(float %27, float %30, float %31)
  store float %32, ptr %3, align 4
  br label %33

33:                                               ; preds = %23
  %34 = load i32, ptr %4, align 4
  %35 = add nsw i32 %34, 1
  store i32 %35, ptr %4, align 4
  br label %20, !llvm.loop !8

36:                                               ; preds = %20
  %37 = load float, ptr %3, align 4
  %38 = fpext float %37 to double
  %39 = call i32 (ptr, ...) @printf(ptr noundef @.str, double noundef %38)
  ret i32 0
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fmuladd.f32(float, float, float) #1

declare i32 @printf(ptr noundef, ...) #2

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

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
