import React from 'react';
import { ExternalLink, Tag } from 'lucide-react';
import { Product } from '@/api/api';

interface ProductCardProps {
    product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
    return (
        <div className="flex-none w-[280px] bg-[#1e1f20]/90 backdrop-blur-md rounded-2xl border border-white/10 overflow-hidden hover:border-primary/50 transition-all duration-300 group shadow-lg">
            <div className="relative h-40 w-full bg-white/5 overflow-hidden">
                {product.image && product.image !== 'No Image' ? (
                    <img
                        src={product.image}
                        alt={product.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                ) : product.link ? (
                    <img
                        src={`https://s0.wp.com/mshots/v1/${encodeURIComponent(product.link)}?w=400`}
                        alt={product.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                ) : (
                    <div className="w-full h-full flex items-center justify-center text-muted-foreground bg-gradient-to-br from-white/5 to-white/10">
                        No Image
                    </div>
                )}
                <div className="absolute top-2 right-2 bg-black/60 backdrop-blur-sm px-2 py-1 rounded-md text-xs font-medium text-white border border-white/10">
                    {product.marketplace}
                </div>
            </div>

            <div className="p-4 flex flex-col h-[180px]">
                <h3 className="text-base font-semibold text-foreground line-clamp-2 mb-1 group-hover:text-primary transition-colors">
                    {product.name}
                </h3>

                <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg font-bold text-primary">{product.price}</span>
                </div>

                {product.reason && (
                    <p className="text-xs text-muted-foreground/80 line-clamp-3 mb-3 italic">
                        "{product.reason}"
                    </p>
                )}

                <div className="mt-auto">
                    <a
                        href={product.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-center w-full gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm font-medium transition-colors border border-white/5 hover:border-white/20"
                    >
                        Buy Now
                        <ExternalLink className="w-3 h-3" />
                    </a>
                </div>
            </div>
        </div>
    );
}
