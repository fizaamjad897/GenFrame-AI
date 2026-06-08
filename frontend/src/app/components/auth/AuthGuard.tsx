"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useUser } from "@/app/context/AuthContext";

export function AuthGuard({ children }: { children: React.ReactNode }) {
    const { user, loading } = useUser();
    const router = useRouter();
    const pathname = usePathname();
    const [isChecking, setIsChecking] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem("auth_token");
        if (!token) {
            router.push("/auth");
            return;
        }

        if (!loading) {
            if (!user) {
                router.push("/auth");
            } else {
                setIsChecking(false);
            }
        }
    }, [user, loading, router, pathname]);

    if (loading || isChecking) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
                <div className="w-8 h-8 rounded-full border-2 border-purple-200 border-t-purple-600 animate-spin"></div>
            </div>
        );
    }

    if (!user) {
        return null;
    }

    return <>{children}</>;
}
