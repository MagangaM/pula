"""Lightweight demo evaluation helpers; not a field-performance claim."""
def confusion_counts(expected, predicted):
    if len(expected)!=len(predicted): raise ValueError("Lists must be equal length")
    tp=sum(e==1 and p==1 for e,p in zip(expected,predicted)); tn=sum(e==0 and p==0 for e,p in zip(expected,predicted))
    fp=sum(e==0 and p==1 for e,p in zip(expected,predicted)); fn=sum(e==1 and p==0 for e,p in zip(expected,predicted))
    return {"tp":tp,"tn":tn,"fp":fp,"fn":fn}
def metrics(counts):
    tp,tn,fp,fn=(counts[k] for k in ("tp","tn","fp","fn"))
    div=lambda a,b: round(a/b,3) if b else None
    return {"precision":div(tp,tp+fp),"recall":div(tp,tp+fn),"specificity":div(tn,tn+fp),"accuracy":div(tp+tn,tp+tn+fp+fn)}
