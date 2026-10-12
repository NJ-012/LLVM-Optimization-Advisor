; ModuleID = '/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/array_transform.c'
source_filename = "/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/array_transform.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@a = internal global [1300000 x double] zeroinitializer, align 16
@b = internal global [1300000 x double] zeroinitializer, align 16
@.str = private unnamed_addr constant [6 x i8] c"%.8f\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  %3 = alloca i32, align 4
  %4 = alloca double, align 8
  %5 = alloca i32, align 4
  store i32 0, ptr %1, align 4
  store i32 0, ptr %2, align 4
  br label %6

6:                                                ; preds = %17, %0
  %7 = load i32, ptr %2, align 4
  %8 = icmp slt i32 %7, 1300000
  br i1 %8, label %9, label %20

9:                                                ; preds = %6
  %10 = load i32, ptr %2, align 4
  %11 = srem i32 %10, 97
  %12 = sitofp i32 %11 to double
  %13 = fmul double %12, 2.000000e-02
  %14 = load i32, ptr %2, align 4
  %15 = sext i32 %14 to i64
  %16 = getelementptr inbounds [1300000 x double], ptr @a, i64 0, i64 %15
  store double %13, ptr %16, align 8
  br label %17

17:                                               ; preds = %9
  %18 = load i32, ptr %2, align 4
  %19 = add nsw i32 %18, 1
  store i32 %19, ptr %2, align 4
  br label %6, !llvm.loop !6

20:                                               ; preds = %6
  store i32 0, ptr %3, align 4
  br label %21

21:                                               ; preds = %43, %20
  %22 = load i32, ptr %3, align 4
  %23 = icmp slt i32 %22, 1300000
  br i1 %23, label %24, label %46

24:                                               ; preds = %21
  %25 = load i32, ptr %3, align 4
  %26 = sext i32 %25 to i64
  %27 = getelementptr inbounds [1300000 x double], ptr @a, i64 0, i64 %26
  %28 = load double, ptr %27, align 8
  %29 = load i32, ptr %3, align 4
  %30 = sext i32 %29 to i64
  %31 = getelementptr inbounds [1300000 x double], ptr @a, i64 0, i64 %30
  %32 = load double, ptr %31, align 8
  %33 = load i32, ptr %3, align 4
  %34 = sext i32 %33 to i64
  %35 = getelementptr inbounds [1300000 x double], ptr @a, i64 0, i64 %34
  %36 = load double, ptr %35, align 8
  %37 = fmul double 2.000000e+00, %36
  %38 = call double @llvm.fmuladd.f64(double %28, double %32, double %37)
  %39 = fadd double %38, 1.000000e+00
  %40 = load i32, ptr %3, align 4
  %41 = sext i32 %40 to i64
  %42 = getelementptr inbounds [1300000 x double], ptr @b, i64 0, i64 %41
  store double %39, ptr %42, align 8
  br label %43

43:                                               ; preds = %24
  %44 = load i32, ptr %3, align 4
  %45 = add nsw i32 %44, 1
  store i32 %45, ptr %3, align 4
  br label %21, !llvm.loop !8

46:                                               ; preds = %21
  store double 0.000000e+00, ptr %4, align 8
  store i32 0, ptr %5, align 4
  br label %47

47:                                               ; preds = %57, %46
  %48 = load i32, ptr %5, align 4
  %49 = icmp slt i32 %48, 1300000
  br i1 %49, label %50, label %60

50:                                               ; preds = %47
  %51 = load i32, ptr %5, align 4
  %52 = sext i32 %51 to i64
  %53 = getelementptr inbounds [1300000 x double], ptr @b, i64 0, i64 %52
  %54 = load double, ptr %53, align 8
  %55 = load double, ptr %4, align 8
  %56 = fadd double %55, %54
  store double %56, ptr %4, align 8
  br label %57

57:                                               ; preds = %50
  %58 = load i32, ptr %5, align 4
  %59 = add nsw i32 %58, 1
  store i32 %59, ptr %5, align 4
  br label %47, !llvm.loop !9

60:                                               ; preds = %47
  %61 = load double, ptr %4, align 8
  %62 = call i32 (ptr, ...) @printf(ptr noundef @.str, double noundef %61)
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
!9 = distinct !{!9, !7}
