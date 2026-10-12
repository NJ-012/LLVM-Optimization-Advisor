; ModuleID = '/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/dot_product.c'
source_filename = "/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/dot_product.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@a = internal global [1600000 x double] zeroinitializer, align 16
@b = internal global [1600000 x double] zeroinitializer, align 16
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

5:                                                ; preds = %23, %0
  %6 = load i32, ptr %2, align 4
  %7 = icmp slt i32 %6, 1600000
  br i1 %7, label %8, label %26

8:                                                ; preds = %5
  %9 = load i32, ptr %2, align 4
  %10 = srem i32 %9, 31
  %11 = sitofp i32 %10 to double
  %12 = fmul double %11, 1.000000e-01
  %13 = load i32, ptr %2, align 4
  %14 = sext i32 %13 to i64
  %15 = getelementptr inbounds [1600000 x double], ptr @a, i64 0, i64 %14
  store double %12, ptr %15, align 8
  %16 = load i32, ptr %2, align 4
  %17 = srem i32 %16, 23
  %18 = sitofp i32 %17 to double
  %19 = fmul double %18, 2.000000e-01
  %20 = load i32, ptr %2, align 4
  %21 = sext i32 %20 to i64
  %22 = getelementptr inbounds [1600000 x double], ptr @b, i64 0, i64 %21
  store double %19, ptr %22, align 8
  br label %23

23:                                               ; preds = %8
  %24 = load i32, ptr %2, align 4
  %25 = add nsw i32 %24, 1
  store i32 %25, ptr %2, align 4
  br label %5, !llvm.loop !6

26:                                               ; preds = %5
  store double 0.000000e+00, ptr %3, align 8
  store i32 0, ptr %4, align 4
  br label %27

27:                                               ; preds = %41, %26
  %28 = load i32, ptr %4, align 4
  %29 = icmp slt i32 %28, 1600000
  br i1 %29, label %30, label %44

30:                                               ; preds = %27
  %31 = load i32, ptr %4, align 4
  %32 = sext i32 %31 to i64
  %33 = getelementptr inbounds [1600000 x double], ptr @a, i64 0, i64 %32
  %34 = load double, ptr %33, align 8
  %35 = load i32, ptr %4, align 4
  %36 = sext i32 %35 to i64
  %37 = getelementptr inbounds [1600000 x double], ptr @b, i64 0, i64 %36
  %38 = load double, ptr %37, align 8
  %39 = load double, ptr %3, align 8
  %40 = call double @llvm.fmuladd.f64(double %34, double %38, double %39)
  store double %40, ptr %3, align 8
  br label %41

41:                                               ; preds = %30
  %42 = load i32, ptr %4, align 4
  %43 = add nsw i32 %42, 1
  store i32 %43, ptr %4, align 4
  br label %27, !llvm.loop !8

44:                                               ; preds = %27
  %45 = load double, ptr %3, align 8
  %46 = call i32 (ptr, ...) @printf(ptr noundef @.str, double noundef %45)
  ret i32 0
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.fmuladd.f64(double, double, double) #1

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
