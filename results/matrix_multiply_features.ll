; ModuleID = '/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/matrix_multiply.c'
source_filename = "/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/matrix_multiply.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@a = internal global [170 x [170 x double]] zeroinitializer, align 16
@b = internal global [170 x [170 x double]] zeroinitializer, align 16
@c = internal global [170 x [170 x double]] zeroinitializer, align 16
@.str = private unnamed_addr constant [6 x i8] c"%.8f\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = alloca i32, align 4
  %6 = alloca i32, align 4
  %7 = alloca double, align 8
  %8 = alloca i32, align 4
  %9 = alloca i32, align 4
  store i32 0, ptr %1, align 4
  store i32 0, ptr %2, align 4
  br label %10

10:                                               ; preds = %53, %0
  %11 = load i32, ptr %2, align 4
  %12 = icmp slt i32 %11, 170
  br i1 %12, label %13, label %56

13:                                               ; preds = %10
  store i32 0, ptr %3, align 4
  br label %14

14:                                               ; preds = %49, %13
  %15 = load i32, ptr %3, align 4
  %16 = icmp slt i32 %15, 170
  br i1 %16, label %17, label %52

17:                                               ; preds = %14
  %18 = load i32, ptr %2, align 4
  %19 = load i32, ptr %3, align 4
  %20 = add nsw i32 %18, %19
  %21 = srem i32 %20, 17
  %22 = sitofp i32 %21 to double
  %23 = fmul double %22, 1.000000e-01
  %24 = load i32, ptr %2, align 4
  %25 = sext i32 %24 to i64
  %26 = getelementptr inbounds [170 x [170 x double]], ptr @a, i64 0, i64 %25
  %27 = load i32, ptr %3, align 4
  %28 = sext i32 %27 to i64
  %29 = getelementptr inbounds [170 x double], ptr %26, i64 0, i64 %28
  store double %23, ptr %29, align 8
  %30 = load i32, ptr %2, align 4
  %31 = mul nsw i32 %30, 3
  %32 = load i32, ptr %3, align 4
  %33 = add nsw i32 %31, %32
  %34 = srem i32 %33, 19
  %35 = sitofp i32 %34 to double
  %36 = fmul double %35, 2.000000e-01
  %37 = load i32, ptr %2, align 4
  %38 = sext i32 %37 to i64
  %39 = getelementptr inbounds [170 x [170 x double]], ptr @b, i64 0, i64 %38
  %40 = load i32, ptr %3, align 4
  %41 = sext i32 %40 to i64
  %42 = getelementptr inbounds [170 x double], ptr %39, i64 0, i64 %41
  store double %36, ptr %42, align 8
  %43 = load i32, ptr %2, align 4
  %44 = sext i32 %43 to i64
  %45 = getelementptr inbounds [170 x [170 x double]], ptr @c, i64 0, i64 %44
  %46 = load i32, ptr %3, align 4
  %47 = sext i32 %46 to i64
  %48 = getelementptr inbounds [170 x double], ptr %45, i64 0, i64 %47
  store double 0.000000e+00, ptr %48, align 8
  br label %49

49:                                               ; preds = %17
  %50 = load i32, ptr %3, align 4
  %51 = add nsw i32 %50, 1
  store i32 %51, ptr %3, align 4
  br label %14, !llvm.loop !6

52:                                               ; preds = %14
  br label %53

53:                                               ; preds = %52
  %54 = load i32, ptr %2, align 4
  %55 = add nsw i32 %54, 1
  store i32 %55, ptr %2, align 4
  br label %10, !llvm.loop !8

56:                                               ; preds = %10
  store i32 0, ptr %4, align 4
  br label %57

57:                                               ; preds = %99, %56
  %58 = load i32, ptr %4, align 4
  %59 = icmp slt i32 %58, 170
  br i1 %59, label %60, label %102

60:                                               ; preds = %57
  store i32 0, ptr %5, align 4
  br label %61

61:                                               ; preds = %95, %60
  %62 = load i32, ptr %5, align 4
  %63 = icmp slt i32 %62, 170
  br i1 %63, label %64, label %98

64:                                               ; preds = %61
  store i32 0, ptr %6, align 4
  br label %65

65:                                               ; preds = %91, %64
  %66 = load i32, ptr %6, align 4
  %67 = icmp slt i32 %66, 170
  br i1 %67, label %68, label %94

68:                                               ; preds = %65
  %69 = load i32, ptr %4, align 4
  %70 = sext i32 %69 to i64
  %71 = getelementptr inbounds [170 x [170 x double]], ptr @a, i64 0, i64 %70
  %72 = load i32, ptr %5, align 4
  %73 = sext i32 %72 to i64
  %74 = getelementptr inbounds [170 x double], ptr %71, i64 0, i64 %73
  %75 = load double, ptr %74, align 8
  %76 = load i32, ptr %5, align 4
  %77 = sext i32 %76 to i64
  %78 = getelementptr inbounds [170 x [170 x double]], ptr @b, i64 0, i64 %77
  %79 = load i32, ptr %6, align 4
  %80 = sext i32 %79 to i64
  %81 = getelementptr inbounds [170 x double], ptr %78, i64 0, i64 %80
  %82 = load double, ptr %81, align 8
  %83 = load i32, ptr %4, align 4
  %84 = sext i32 %83 to i64
  %85 = getelementptr inbounds [170 x [170 x double]], ptr @c, i64 0, i64 %84
  %86 = load i32, ptr %6, align 4
  %87 = sext i32 %86 to i64
  %88 = getelementptr inbounds [170 x double], ptr %85, i64 0, i64 %87
  %89 = load double, ptr %88, align 8
  %90 = call double @llvm.fmuladd.f64(double %75, double %82, double %89)
  store double %90, ptr %88, align 8
  br label %91

91:                                               ; preds = %68
  %92 = load i32, ptr %6, align 4
  %93 = add nsw i32 %92, 1
  store i32 %93, ptr %6, align 4
  br label %65, !llvm.loop !9

94:                                               ; preds = %65
  br label %95

95:                                               ; preds = %94
  %96 = load i32, ptr %5, align 4
  %97 = add nsw i32 %96, 1
  store i32 %97, ptr %5, align 4
  br label %61, !llvm.loop !10

98:                                               ; preds = %61
  br label %99

99:                                               ; preds = %98
  %100 = load i32, ptr %4, align 4
  %101 = add nsw i32 %100, 1
  store i32 %101, ptr %4, align 4
  br label %57, !llvm.loop !11

102:                                              ; preds = %57
  store double 0.000000e+00, ptr %7, align 8
  store i32 0, ptr %8, align 4
  br label %103

103:                                              ; preds = %130, %102
  %104 = load i32, ptr %8, align 4
  %105 = icmp slt i32 %104, 170
  br i1 %105, label %106, label %133

106:                                              ; preds = %103
  store i32 0, ptr %9, align 4
  br label %107

107:                                              ; preds = %126, %106
  %108 = load i32, ptr %9, align 4
  %109 = icmp slt i32 %108, 170
  br i1 %109, label %110, label %129

110:                                              ; preds = %107
  %111 = load i32, ptr %8, align 4
  %112 = sext i32 %111 to i64
  %113 = getelementptr inbounds [170 x [170 x double]], ptr @c, i64 0, i64 %112
  %114 = load i32, ptr %9, align 4
  %115 = sext i32 %114 to i64
  %116 = getelementptr inbounds [170 x double], ptr %113, i64 0, i64 %115
  %117 = load double, ptr %116, align 8
  %118 = load i32, ptr %8, align 4
  %119 = mul nsw i32 %118, 170
  %120 = add nsw i32 1, %119
  %121 = load i32, ptr %9, align 4
  %122 = add nsw i32 %120, %121
  %123 = sitofp i32 %122 to double
  %124 = load double, ptr %7, align 8
  %125 = call double @llvm.fmuladd.f64(double %117, double %123, double %124)
  store double %125, ptr %7, align 8
  br label %126

126:                                              ; preds = %110
  %127 = load i32, ptr %9, align 4
  %128 = add nsw i32 %127, 1
  store i32 %128, ptr %9, align 4
  br label %107, !llvm.loop !12

129:                                              ; preds = %107
  br label %130

130:                                              ; preds = %129
  %131 = load i32, ptr %8, align 4
  %132 = add nsw i32 %131, 1
  store i32 %132, ptr %8, align 4
  br label %103, !llvm.loop !13

133:                                              ; preds = %103
  %134 = load double, ptr %7, align 8
  %135 = call i32 (ptr, ...) @printf(ptr noundef @.str, double noundef %134)
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
!13 = distinct !{!13, !7}
