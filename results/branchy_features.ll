; ModuleID = '/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/branchy.c'
source_filename = "/mnt/d/Projects/adaptive_llvm_advisor_final/benchmarks/branchy.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@.str = private unnamed_addr constant [6 x i8] c"%lld\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca i64, align 8
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  store i32 0, ptr %1, align 4
  store i64 0, ptr %2, align 8
  store i32 0, ptr %3, align 4
  br label %5

5:                                                ; preds = %36, %0
  %6 = load i32, ptr %3, align 4
  %7 = icmp slt i32 %6, 5000000
  br i1 %7, label %8, label %39

8:                                                ; preds = %5
  %9 = load i32, ptr %3, align 4
  %10 = mul nsw i32 %9, 37
  %11 = srem i32 %10, 101
  store i32 %11, ptr %4, align 4
  %12 = load i32, ptr %4, align 4
  %13 = icmp slt i32 %12, 25
  br i1 %13, label %14, label %20

14:                                               ; preds = %8
  %15 = load i32, ptr %4, align 4
  %16 = mul nsw i32 %15, 3
  %17 = sext i32 %16 to i64
  %18 = load i64, ptr %2, align 8
  %19 = add nsw i64 %18, %17
  store i64 %19, ptr %2, align 8
  br label %35

20:                                               ; preds = %8
  %21 = load i32, ptr %4, align 4
  %22 = icmp slt i32 %21, 70
  br i1 %22, label %23, label %29

23:                                               ; preds = %20
  %24 = load i32, ptr %4, align 4
  %25 = sdiv i32 %24, 2
  %26 = sext i32 %25 to i64
  %27 = load i64, ptr %2, align 8
  %28 = sub nsw i64 %27, %26
  store i64 %28, ptr %2, align 8
  br label %34

29:                                               ; preds = %20
  %30 = load i32, ptr %4, align 4
  %31 = sext i32 %30 to i64
  %32 = load i64, ptr %2, align 8
  %33 = add nsw i64 %32, %31
  store i64 %33, ptr %2, align 8
  br label %34

34:                                               ; preds = %29, %23
  br label %35

35:                                               ; preds = %34, %14
  br label %36

36:                                               ; preds = %35
  %37 = load i32, ptr %3, align 4
  %38 = add nsw i32 %37, 1
  store i32 %38, ptr %3, align 4
  br label %5, !llvm.loop !6

39:                                               ; preds = %5
  %40 = load i64, ptr %2, align 8
  %41 = call i32 (ptr, ...) @printf(ptr noundef @.str, i64 noundef %40)
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
