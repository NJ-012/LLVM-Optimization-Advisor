; ModuleID = '/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/matrix_transpose.c'
source_filename = "/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/matrix_transpose.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@a = internal global [700 x [700 x double]] zeroinitializer, align 16
@b = internal global [700 x [700 x double]] zeroinitializer, align 16
@.str = private unnamed_addr constant [6 x i8] c"%.8f\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = alloca i32, align 4
  %6 = alloca double, align 8
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  store i32 0, ptr %1, align 4
  store i32 0, ptr %2, align 4
  br label %9

9:                                                ; preds = %33, %0
  %10 = load i32, ptr %2, align 4
  %11 = icmp slt i32 %10, 700
  br i1 %11, label %12, label %36

12:                                               ; preds = %9
  store i32 0, ptr %3, align 4
  br label %13

13:                                               ; preds = %29, %12
  %14 = load i32, ptr %3, align 4
  %15 = icmp slt i32 %14, 700
  br i1 %15, label %16, label %32

16:                                               ; preds = %13
  %17 = load i32, ptr %2, align 4
  %18 = load i32, ptr %3, align 4
  %19 = add nsw i32 %17, %18
  %20 = srem i32 %19, 101
  %21 = sitofp i32 %20 to double
  %22 = fmul double %21, 1.000000e-02
  %23 = load i32, ptr %2, align 4
  %24 = sext i32 %23 to i64
  %25 = getelementptr inbounds [700 x [700 x double]], ptr @a, i64 0, i64 %24
  %26 = load i32, ptr %3, align 4
  %27 = sext i32 %26 to i64
  %28 = getelementptr inbounds [700 x double], ptr %25, i64 0, i64 %27
  store double %22, ptr %28, align 8
  br label %29

29:                                               ; preds = %16
  %30 = load i32, ptr %3, align 4
  %31 = add nsw i32 %30, 1
  store i32 %31, ptr %3, align 4
  br label %13, !llvm.loop !6

32:                                               ; preds = %13
  br label %33

33:                                               ; preds = %32
  %34 = load i32, ptr %2, align 4
  %35 = add nsw i32 %34, 1
  store i32 %35, ptr %2, align 4
  br label %9, !llvm.loop !8

36:                                               ; preds = %9
  store i32 0, ptr %4, align 4
  br label %37

37:                                               ; preds = %62, %36
  %38 = load i32, ptr %4, align 4
  %39 = icmp slt i32 %38, 700
  br i1 %39, label %40, label %65

40:                                               ; preds = %37
  store i32 0, ptr %5, align 4
  br label %41

41:                                               ; preds = %58, %40
  %42 = load i32, ptr %5, align 4
  %43 = icmp slt i32 %42, 700
  br i1 %43, label %44, label %61

44:                                               ; preds = %41
  %45 = load i32, ptr %4, align 4
  %46 = sext i32 %45 to i64
  %47 = getelementptr inbounds [700 x [700 x double]], ptr @a, i64 0, i64 %46
  %48 = load i32, ptr %5, align 4
  %49 = sext i32 %48 to i64
  %50 = getelementptr inbounds [700 x double], ptr %47, i64 0, i64 %49
  %51 = load double, ptr %50, align 8
  %52 = load i32, ptr %5, align 4
  %53 = sext i32 %52 to i64
  %54 = getelementptr inbounds [700 x [700 x double]], ptr @b, i64 0, i64 %53
  %55 = load i32, ptr %4, align 4
  %56 = sext i32 %55 to i64
  %57 = getelementptr inbounds [700 x double], ptr %54, i64 0, i64 %56
  store double %51, ptr %57, align 8
  br label %58

58:                                               ; preds = %44
  %59 = load i32, ptr %5, align 4
  %60 = add nsw i32 %59, 1
  store i32 %60, ptr %5, align 4
  br label %41, !llvm.loop !9

61:                                               ; preds = %41
  br label %62

62:                                               ; preds = %61
  %63 = load i32, ptr %4, align 4
  %64 = add nsw i32 %63, 1
  store i32 %64, ptr %4, align 4
  br label %37, !llvm.loop !10

65:                                               ; preds = %37
  store double 0.000000e+00, ptr %6, align 8
  store i32 0, ptr %7, align 4
  br label %66

66:                                               ; preds = %93, %65
  %67 = load i32, ptr %7, align 4
  %68 = icmp slt i32 %67, 700
  br i1 %68, label %69, label %96

69:                                               ; preds = %66
  store i32 0, ptr %8, align 4
  br label %70

70:                                               ; preds = %89, %69
  %71 = load i32, ptr %8, align 4
  %72 = icmp slt i32 %71, 700
  br i1 %72, label %73, label %92

73:                                               ; preds = %70
  %74 = load i32, ptr %7, align 4
  %75 = sext i32 %74 to i64
  %76 = getelementptr inbounds [700 x [700 x double]], ptr @b, i64 0, i64 %75
  %77 = load i32, ptr %8, align 4
  %78 = sext i32 %77 to i64
  %79 = getelementptr inbounds [700 x double], ptr %76, i64 0, i64 %78
  %80 = load double, ptr %79, align 8
  %81 = load i32, ptr %7, align 4
  %82 = mul nsw i32 %81, 700
  %83 = add nsw i32 1, %82
  %84 = load i32, ptr %8, align 4
  %85 = add nsw i32 %83, %84
  %86 = sitofp i32 %85 to double
  %87 = load double, ptr %6, align 8
  %88 = call double @llvm.fmuladd.f64(double %80, double %86, double %87)
  store double %88, ptr %6, align 8
  br label %89

89:                                               ; preds = %73
  %90 = load i32, ptr %8, align 4
  %91 = add nsw i32 %90, 1
  store i32 %91, ptr %8, align 4
  br label %70, !llvm.loop !11

92:                                               ; preds = %70
  br label %93

93:                                               ; preds = %92
  %94 = load i32, ptr %7, align 4
  %95 = add nsw i32 %94, 1
  store i32 %95, ptr %7, align 4
  br label %66, !llvm.loop !12

96:                                               ; preds = %66
  %97 = load double, ptr %6, align 8
  %98 = call i32 (ptr, ...) @printf(ptr noundef @.str, double noundef %97)
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
!11 = distinct !{!11, !7}
!12 = distinct !{!12, !7}
