#pragma once

#include<iostream>
#include<iterator>
#include<cassert>
#include "RingBufferQueue.hpp"

namespace implicit_twostackslite {
    using namespace std;

    template<typename aggT>
    class __AggT {
    public:
        aggT _val;
        __AggT() {}
        __AggT(aggT val_)
            : _val(val_) {}
    };

    template<typename binOpFunc,
           typename queueT=RingBufferQueue<__AggT<typename binOpFunc::Partial>>>
    class Aggregate {
    public:
        typedef typename binOpFunc::In inT;
        typedef typename binOpFunc::Partial aggT;
        typedef typename binOpFunc::Out outT;
        typedef __AggT<aggT> AggT;

        Aggregate(binOpFunc binOp_, aggT identE_) 
            : _q(), _binOp(binOp_), _backSum(identE_), _identE(identE_) {}

        size_t size() { return _q.size(); }

        void insert(inT v) {
            aggT lifted = _binOp.lift(v);
            _backSum = _binOp.combine(_backSum, lifted);
            _q.push_back(AggT(lifted));
        }

        void evict() { 
            if (_q.begin() == _split) {
                // front is empty, let's turn the "stack" implicity.
                iterT front = _q.begin();
                iterT it = _q.end();
                aggT running_sum = _identE;
                while (it != front) {
                    --it;
                    running_sum = _binOp.combine(it->_val, running_sum);
                    it->_val = running_sum;
                }
                _split = _q.end();
                _backSum = _identE;
            }
            _q.pop_front();
        }

        outT query() {
            auto bp = _backSum;
            auto fp = _q.size()>0?_q.front()._val:_identE;

            // std::cerr << "prequery: " << _binOp.combine(fp, bp) << std::endl;
            auto answer = _binOp.lower(_binOp.combine(fp, bp));
            // std::cerr << "query: " << bp << "--" << fp << "--" << answer << std::endl;
            return  answer;
        }
    private:
        queueT _q;
        typedef typename queueT::iterator iterT;
        iterT _split;
        // the binary operator deck
        binOpFunc _binOp;
        aggT _backSum;
        aggT _identE;
    };

    template <class BinaryFunction, class T>
    Aggregate<BinaryFunction> make_aggregate(BinaryFunction f, T elem) {
        return Aggregate<BinaryFunction>(f, elem);
    }

    template <typename BinaryFunction>
    struct MakeAggregate {
        template <typename T>
        Aggregate<BinaryFunction> operator()(T elem) {
            BinaryFunction f;
            return make_aggregate(f, elem);
        }
    };
}