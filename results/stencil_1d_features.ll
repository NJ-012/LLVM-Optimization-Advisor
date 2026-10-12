; ModuleID = '/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/stencil_1d.c'
source_filename = "/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/stencil_1d.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@a = internal global [500000 x double] zeroinitializer, align 16
@b = internal global [500000 x double] zeroinitializer, align 16
@.str = private unnamed_addr constant [6 x i8] c"%.8f\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = alloca i32, align 4
  store i32 0, ptr %1, align 4
  store i32 0, ptr %2, align 4
  br label %6

6:                                                ; preds = %17, %0
  %7 = load i32, ptr %2, align 4
  %8 = icmp slt i32 %7, 500000
  br i1 %8, label %9, label %20

9:                                                ; preds = %6
  %10 = load i32, ptr %2, align 4
  %11 = srem i32 %10, 101
  %12 = sitofp i32 %11 to double
  %13 = fmul double %12, 1.000000e-02
  %14 = load i32, ptr %2, align 4
  %15 = sext i32 %14 to i64
  %16 = getelementptr inbounds [500000 x double], ptr @a, i64 0, i64 %15
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

21:                                               ; preds = %70, %20
  %22 = load i32, ptr %3, align 4
  %23 = icmp slt i32 %22, 18
  br i1 %23, label %24, label %73

24:                                               ; preds = %21
  %25 = load double, ptr @a, align 16
  store double %25, ptr @b, align 16
  %26 = load double, ptr getelementptr inbounds ([500000 x double], ptr @a, i64 0, i64 499999), align 8
  store double %26, ptr getelementptr inbounds ([500000 x double], ptr @b, i64 0, i64 499999), align 8
  store i32 1, ptr %4, align 4
  br label %27

27:                                               ; preds = %51, %24
  %28 = load i32, ptr %4, align 4
  %29 = icmp slt i32 %28, 499999
  br i1 %29, label %30, label %54

30:                                               ; preds = %27
  %31 = load i32, ptr %4, align 4
  %32 = sub nsw i32 %31, 1
  %33 = sext i32 %32 to i64
  %34 = getelementptr inbounds [500000 x double], ptr @a, i64 0, i64 %33
  %35 = load double, ptr %34, align 8
  %36 = load i32, ptr %4, align 4
  %37 = sext i32 %36 to i64
  %38 = getelementptr inbounds [500000 x double], ptr @a, i64 0, i64 %37
  %39 = load double, ptr %38, align 8
  %40 = fmul double 5.000000e-01, %39
  %41 = call double @llvm.fmuladd.f64(double 2.500000e-01, double %35, double %40)
  %42 = load i32, ptr %4, align 4
  %43 = add nsw i32 %42, 1
  %44 = sext i32 %43 to i64
  %45 = getelementptr inbounds [500000 x double], ptr @a, i64 0, i64 %44
  %46 = load double, ptr %45, align 8
  %47 = call double @llvm.fmuladd.f64(double 2.500000e-01, double %46, double %41)
  %48 = load i32, ptr %4, align 4
  %49 = sext i32 %48 to i64
  %50 = getelementptr inbounds [500000 x double], ptr @b, i64 0, i64 %49
  store double %47, ptr %50, align 8
  br label %51

51:                                               ; preds = %30
  %52 = load i32, ptr %4, align 4
  %53 = add nsw i32 %52, 1
  store i32 %53, ptr %4, align 4
  br label %27, !llvm.loop !8

54:                                               ; preds = %27
  store i32 0, ptr %5, align 4
  br label %55

55:                                               ; preds = %66, %54
  %56 = load i32, ptr %5, align 4
  %57 = icmp slt i32 %56, 500000
  br i1 %57, label %58, label %69

58:                                               ; preds = %55
  %59 = load i32, ptr %5, align 4
  %60 = sext i32 %59 to i64
  %61 = getelementptr inbounds [500000 x double], ptr @b, i64 0, i64 %60
  %62 = load double, ptr %61, align 8
  %63 = load i32, ptr %5, align 4
  %64 = sext i32 %63 to i64
  %65 = getelementptr inbounds [500000 x double], ptr @a, i64 0, i64 %64
  store double %62, ptr %65, align 8
  br label %66

66:                                               ; preds = %58
  %67 = load i32, ptr %5, align 4
  %68 = add nsw i32 %67, 1
  store i32 %68, ptr %5, align 4
  br label %55, !llvm.loop !9

69:                                               ; preds = %55
  br label %70

70:                                               ; preds = %69
  %71 = load i32, ptr %3, align 4
  %72 = add nsw i32 %71, 1
  store i32 %72, ptr %3, align 4
  br label %21, !llvm.loop !10

73:                                               ; preds = %21
  %74 = load double, ptr getelementptr inbounds ([500000 x double], ptr @a, i64 0, i64 250000), align 16
  %75 = call i32 (ptr, ...) @printf(ptr noundef @.str, double noundef %74)
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
!10 = distinct !{!10, !7}
