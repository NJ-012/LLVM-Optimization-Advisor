; ModuleID = '/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/conditional_count.c'
source_filename = "/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/conditional_count.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@.str = private unnamed_addr constant [11 x i8] c"%lld %lld\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca i64, align 8
  %3 = alloca i64, align 8
  %4 = alloca i32, align 4
  %5 = alloca i32, align 4
  store i32 0, ptr %1, align 4
  store i64 0, ptr %2, align 8
  store i64 0, ptr %3, align 8
  store i32 0, ptr %4, align 4
  br label %6

6:                                                ; preds = %29, %0
  %7 = load i32, ptr %4, align 4
  %8 = icmp slt i32 %7, 7000000
  br i1 %8, label %9, label %32

9:                                                ; preds = %6
  %10 = load i32, ptr %4, align 4
  %11 = mul nsw i32 %10, 17
  %12 = add nsw i32 %11, 13
  %13 = srem i32 %12, 257
  store i32 %13, ptr %5, align 4
  %14 = load i32, ptr %5, align 4
  %15 = and i32 %14, 1
  %16 = icmp ne i32 %15, 0
  br i1 %16, label %17, label %20

17:                                               ; preds = %9
  %18 = load i64, ptr %2, align 8
  %19 = add nsw i64 %18, 1
  store i64 %19, ptr %2, align 8
  br label %20

20:                                               ; preds = %17, %9
  %21 = load i32, ptr %5, align 4
  %22 = icmp sgt i32 %21, 128
  br i1 %22, label %23, label %28

23:                                               ; preds = %20
  %24 = load i32, ptr %5, align 4
  %25 = sext i32 %24 to i64
  %26 = load i64, ptr %3, align 8
  %27 = add nsw i64 %26, %25
  store i64 %27, ptr %3, align 8
  br label %28

28:                                               ; preds = %23, %20
  br label %29

29:                                               ; preds = %28
  %30 = load i32, ptr %4, align 4
  %31 = add nsw i32 %30, 1
  store i32 %31, ptr %4, align 4
  br label %6, !llvm.loop !6

32:                                               ; preds = %6
  %33 = load i64, ptr %2, align 8
  %34 = load i64, ptr %3, align 8
  %35 = call i32 (ptr, ...) @printf(ptr noundef @.str, i64 noundef %33, i64 noundef %34)
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
